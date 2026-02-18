from django.urls import path
from django.contrib.auth.views import LoginView, PasswordChangeView, PasswordChangeDoneView

from .views import RegisterView, registration_success, BiographyUpdateView, deletion_success
from . import views

app_name = 'users'
urlpatterns = [
    path('', views.BloggerListView.as_view(), name='user-list'),
    path('registration/', RegisterView.as_view(), name='registration'),
    path('registration-success/', registration_success, name='registration-success'),
    path('login/', LoginView.as_view(), name='login'),
    path('password-change-done/', PasswordChangeDoneView.as_view(), name='password-change-done'),
    path('deleted-user/', views.deleted_profile, name='user-deleted-profile'),
    path('deletion-success/', deletion_success, name='deletion-success'),
    path('password-change/', PasswordChangeView.as_view(success_url='users:password-change-done'), name='password-change'),
    path('biography-update/', BiographyUpdateView.as_view(), name='biography-update'),
    path('profile/<str:username>/', views.BloggerDetailView.as_view(), name='user-detail'),
    path('user-delete/', views.BloggerDeleteView.as_view(), name='user-delete'),
]