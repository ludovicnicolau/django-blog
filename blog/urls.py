from django.urls import path

from . import views

app_name = 'blog'
urlpatterns = [
    path('', views.home, name='home'),
    path('blogs/', views.BlogPostListView.as_view(), name='blogs'),
    path('<int:pk>/', views.BlogPostDetailView.as_view(), name='blog-detail'),
    path('<int:pk>/create/', views.CommentCreateView.as_view(), name='comment-form'),
    path('create/', views.BlogPostCreateView.as_view(), name='blog-create'),
    path('<int:pk>/update/', views.BlogPostUpdateView.as_view(), name='blog-update'),
    path('<int:pk>/delete/', views.BlogPostDeleteView.as_view(), name='blog-delete'),
]