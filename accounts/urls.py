from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    # Authentication URLs (also available at root level for convenience)
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.signup_view, name='register'),
    path('password_reset/', views.forgot_password, name='password_reset'),
    path('reset-password/<str:token>/', views.reset_password, name='reset_password_token'),
    path('verify-email/', views.verify_email, name='verify_email'),
    path('verify-email/<str:token>/', views.verify_email, name='verify_email_token'),
    
    # Account management URLs
    path('profile/', views.profile_view, name='profile'),
    path('change-password/', views.change_password_view, name='change_password'),
]
