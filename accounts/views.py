from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model

from .models import User
from .serializers import (
    UserSerializer,
    RegisterSerializer,
    CustomTokenObtainPairSerializer,
    UpdateProfileSerializer
)

UserModel = get_user_model()


class RegisterView(viewsets.GenericViewSet):
    """ViewSet para registro de usuarios"""
    
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]
    
    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Generar tokens JWT
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'user': UserSerializer(user, context={'request': request}).data,
            'access': str(refresh.access_token),
            'refresh': str(refresh)
        }, status=status.HTTP_201_CREATED)


class CustomTokenObtainPairView(TokenObtainPairView):
    """View para login con tokens JWT"""
    serializer_class = CustomTokenObtainPairSerializer


class UserProfileViewSet(viewsets.ModelViewSet):
    """ViewSet para gestión de perfil de usuario"""
    
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return UserModel.objects.filter(id=self.request.user.id)
    
    def get_serializer_class(self):
        if self.action in ['update', 'partial_update']:
            return UpdateProfileSerializer
        return UserSerializer
    
    @action(detail=False, methods=['get', 'put', 'patch'], url_path='me')
    def me(self, request):
        """Obtener o actualizar perfil del usuario autenticado"""
        if request.method == 'GET':
            serializer = self.get_serializer(request.user, context={'request': request})
            return Response(serializer.data)
        
        # PUT o PATCH - Actualizar perfil
        partial = request.method == 'PATCH'
        serializer = self.get_serializer(
            request.user,
            data=request.data,
            partial=partial,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        # Usar el serializer con contexto para obtener la URL absoluta de la foto
        user_serializer = UserSerializer(request.user, context={'request': request})
        return Response(user_serializer.data)
    
    
    @action(detail=False, methods=['post'], url_path='logout')
    def logout(self, request):
        """Logout del usuario"""
        try:
            refresh_token = request.data.get('refresh')
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({'message': 'Logout exitoso'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {'error': 'Token inválido'},
                status=status.HTTP_400_BAD_REQUEST
            )
