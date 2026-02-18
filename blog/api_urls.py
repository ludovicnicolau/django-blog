from django.urls import path
from rest_framework.routers import DefaultRouter

from . import api_views

app_name = 'api-blog'

urlpatterns = [
    
]

router = DefaultRouter()
router.register('blogposts', api_views.BlogPostAPIViewSet, basename='blogpost')

urlpatterns += router.urls