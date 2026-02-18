from django.urls import path

from . import api_views

urlpatterns = [
    path('bloggers/', api_views.BloggerListAPIView.as_view(), name='blogger-list'),
    path('bloggers/<str:username>/', api_views.BloggerRetrieveAPIView.as_view(), name='blogger-detail'),
]
