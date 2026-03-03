from django.urls import path

from . import views

app_name = 'blog'
urlpatterns = [
    path('', views.home, name='home'),
    path('blogs/', views.BlogPostListView.as_view(), name='blogs'),
    path('categories/', views.CategoryListView.as_view(), name='category-list'),
    path('categories/<str:name>/', views.CategoryDetailView.as_view(), name='category-detail'),
    # path('<int:pk>/', views.BlogPostDetailView.as_view(), name='blog-detail'),
    path('create/', views.BlogPostCreateView.as_view(), name='blog-create'),
    path('<slug:slug>/', views.BlogPostDetailView.as_view(), name='blog-detail'),
    path('<slug:slug>/create/', views.CommentCreateView.as_view(), name='comment-form'),
    path('<slug:slug>/update/', views.BlogPostUpdateView.as_view(), name='blog-update'),
    path('<slug:slug>/delete/', views.BlogPostDeleteView.as_view(), name='blog-delete'),
]