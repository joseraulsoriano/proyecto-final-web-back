from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    RegisterView,
    CustomTokenObtainPairView,
    UserProfileViewSet
)

router = DefaultRouter()
router.register(r'users', UserProfileViewSet, basename='user-profile')

urlpatterns = [
    path('auth/register/', RegisterView.as_view({'post': 'create'}), name='register'),
    path('auth/login/', CustomTokenObtainPairView.as_view(), name='login'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('', include(router.urls)),
]

