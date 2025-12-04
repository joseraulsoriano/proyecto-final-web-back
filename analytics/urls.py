from django.urls import path
from .views import statistics, category_stats

urlpatterns = [
    path('', statistics, name='statistics'),
    path('category/<int:category_id>/', category_stats, name='category-stats'),
]


