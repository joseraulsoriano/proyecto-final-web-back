from django.db import models
from django.core.validators import MinLengthValidator
from accounts.models import User
from categories.models import Category


class Tag(models.Model):
    """Etiquetas opcionales para clasificar posts"""
    name = models.CharField(max_length=50, unique=True, verbose_name='Nombre')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Etiqueta'
        verbose_name_plural = 'Etiquetas'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Post(models.Model):
    class Status(models.TextChoices):
        PUBLISHED = 'PUBLISHED', 'Publicado'
        DRAFT = 'DRAFT', 'Borrador'
        ARCHIVED = 'ARCHIVED', 'Archivado'
    
    title = models.CharField(
        max_length=200,
        validators=[MinLengthValidator(5)],
        verbose_name='Título'
    )
    content = models.TextField(
        validators=[MinLengthValidator(20)],
        verbose_name='Contenido'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name='posts',
        verbose_name='Categoría'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Autor'
    )
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.DRAFT,
        verbose_name='Estado'
    )
    tags = models.ManyToManyField(
        Tag,
        blank=True,
        related_name='posts',
        verbose_name='Etiquetas'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de creación')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Fecha de actualización')
    
    class Meta:
        verbose_name = 'Publicación'
        verbose_name_plural = 'Publicaciones'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at', 'status']),
            models.Index(fields=['category', 'status']),
        ]
    
    def __str__(self):
        return self.title
    
    @property
    def comments_count(self):
        return self.comments.count()
