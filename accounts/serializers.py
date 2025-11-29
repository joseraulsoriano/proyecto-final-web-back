from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth.password_validation import validate_password
from django.conf import settings
from .models import User


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Serializer personalizado para obtener tokens JWT con datos del usuario"""
    
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['email'] = user.email
        token['role'] = user.role
        token['full_name'] = user.get_full_name()
        return token
    
    def validate(self, attrs):
        data = super().validate(attrs)
        request = self.context.get('request')
        data['user'] = UserSerializer(self.user, context={'request': request}).data
        return data


class UserSerializer(serializers.ModelSerializer):
    """Serializer para mostrar datos del usuario"""
    
    full_name = serializers.SerializerMethodField()
    profile_picture = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'full_name', 
                 'role', 'profile_picture', 'date_joined', 'is_active']
        read_only_fields = ['id', 'date_joined', 'is_active']
    
    def get_full_name(self, obj):
        return obj.get_full_name()
    
    def get_profile_picture(self, obj):
        if obj.profile_picture:
            request = self.context.get('request')
            if request:
                # Construir URL absoluta usando el request
                # request.build_absolute_uri() construye la URL completa con el dominio del servidor
                return request.build_absolute_uri(obj.profile_picture.url)
            # Si no hay request (fallback), usar el dominio del servidor desde settings
            # En producción, esto debería estar configurado en ALLOWED_HOSTS
            if hasattr(obj.profile_picture, 'url'):
                # Obtener el dominio del servidor desde settings o usar el host del request
                base_url = getattr(settings, 'BASE_URL', 'http://localhost:8001')
                return f"{base_url}{obj.profile_picture.url}"
            return None
        return None


class RegisterSerializer(serializers.ModelSerializer):
    """Serializer para registro de usuarios"""
    
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password]
    )
    password2 = serializers.CharField(write_only=True, required=True)
    
    class Meta:
        model = User
        fields = ['email', 'password', 'password2', 'first_name', 
                 'last_name', 'role']
        extra_kwargs = {
            'email': {'required': True},
            'first_name': {'required': True},
            'last_name': {'required': True},
        }
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({
                "password": "Las contraseñas no coinciden"
            })
        
        # Validar que el rol sea válido para registro
        if attrs.get('role') and attrs['role'] not in [User.Role.PROFESSOR, User.Role.STUDENT]:
            raise serializers.ValidationError({
                "role": "El rol debe ser PROFESSOR o STUDENT"
            })
        
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password2')
        password = validated_data.pop('password')
        user = User.objects.create_user(password=password, **validated_data)
        return user


class UpdateProfileSerializer(serializers.ModelSerializer):
    """Serializer para actualizar perfil de usuario"""
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'profile_picture']
    
    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

