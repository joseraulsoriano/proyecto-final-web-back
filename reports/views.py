from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.db.models import Q
from .models import Report
from .serializers import ReportSerializer
from .permissions import IsModerator


class ReportViewSet(viewsets.ModelViewSet):
    serializer_class = ReportSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        queryset = Report.objects.select_related(
            'reported_by', 'reviewed_by', 'post', 'comment'
        )
        
        # Moderadores ven todos los reportes
        if user.role in ['ADMIN', 'PROFESSOR']:
            status_filter = self.request.query_params.get('status')
            if status_filter:
                queryset = queryset.filter(status=status_filter)
            else:
                # Por defecto, mostrar pendientes y revisados
                queryset = queryset.filter(status__in=['PENDING', 'REVIEWED'])
        else:
            # Usuarios normales solo ven sus propios reportes
            queryset = queryset.filter(reported_by=user)
        
        return queryset.order_by('-created_at')
    
    def get_permissions(self):
        if self.action in ['review', 'resolve', 'dismiss']:
            return [IsModerator()]
        return super().get_permissions()
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
    
    @action(detail=True, methods=['post'], url_path='review')
    def review(self, request, pk=None):
        """Marcar reporte como revisado"""
        report = self.get_object()
        report.status = Report.Status.REVIEWED
        report.reviewed_by = request.user
        report.reviewed_at = timezone.now()
        report.save()
        return Response(ReportSerializer(report).data)
    
    @action(detail=True, methods=['post'], url_path='resolve')
    def resolve(self, request, pk=None):
        """Resolver reporte (archivar/eliminar contenido)"""
        report = self.get_object()
        action_taken = request.data.get('action_taken', '')
        
        # Archivar o eliminar contenido según el tipo
        if report.type == 'POST' and report.post:
            if 'archive' in action_taken.lower():
                report.post.status = 'ARCHIVED'
                report.post.save()
            elif 'delete' in action_taken.lower():
                report.post.delete()
        
        elif report.type == 'COMMENT' and report.comment:
            if 'delete' in action_taken.lower():
                report.comment.delete()
        
        report.status = Report.Status.RESOLVED
        report.reviewed_by = request.user
        report.reviewed_at = timezone.now()
        report.action_taken = action_taken
        report.save()
        
        return Response(ReportSerializer(report).data)
    
    @action(detail=True, methods=['post'], url_path='dismiss')
    def dismiss(self, request, pk=None):
        """Descartar reporte (sin acción)"""
        report = self.get_object()
        report.status = Report.Status.DISMISSED
        report.reviewed_by = request.user
        report.reviewed_at = timezone.now()
        report.action_taken = request.data.get('action_taken', 'Reporte descartado')
        report.save()
        return Response(ReportSerializer(report).data)
