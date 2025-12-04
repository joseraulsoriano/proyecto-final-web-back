from django.db import models
from django.core.exceptions import ValidationError
from accounts.models import User
from posts.models import Post
from comments.models import Comment


class Report(models.Model):
    class Type(models.TextChoices):
        POST = 'POST', 'Publicación'
        COMMENT = 'COMMENT', 'Comentario'
    
    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pendiente'
        REVIEWED = 'REVIEWED', 'Revisado'
        RESOLVED = 'RESOLVED', 'Resuelto'
        DISMISSED = 'DISMISSED', 'Descartado'
    
    type = models.CharField(max_length=10, choices=Type.choices, verbose_name='Tipo')
    reported_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reports_made',
        verbose_name='Reportado por'
    )
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='reports',
        verbose_name='Publicación'
    )
    comment = models.ForeignKey(
        Comment,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='reports',
        verbose_name='Comentario'
    )
    reason = models.TextField(verbose_name='Motivo del reporte')
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.PENDING,
        verbose_name='Estado'
    )
    reviewed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reports_reviewed',
        verbose_name='Revisado por'
    )
    action_taken = models.TextField(null=True, blank=True, verbose_name='Acción tomada')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de creación')
    reviewed_at = models.DateTimeField(null=True, blank=True, verbose_name='Fecha de revisión')
    
    class Meta:
        verbose_name = 'Reporte'
        verbose_name_plural = 'Reportes'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', '-created_at']),
        ]
    
    def __str__(self):
        return f"Reporte {self.type} - {self.status}"
    
    def clean(self):
        if self.type == 'POST' and not self.post:
            raise ValidationError('Debe seleccionar una publicación')
        if self.type == 'COMMENT' and not self.comment:
            raise ValidationError('Debe seleccionar un comentario')
        super().clean()
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
