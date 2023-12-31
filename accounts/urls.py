from django.urls import path
from . import views

app_name = "accounts"
urlpatterns = [
    path('login/', views.UserLogin.as_view(), name='login'),
    path('login/refresh/', views.RefreshToken.as_view(), name='token_refresh'),
    path('register/', views.UserRegister.as_view(), name='register'),
    path('verify_account_request/', views.VerifyAccountRequestView.as_view(), name='verify_account_request'),
    path('verify_account/<str:uidb64>/<str:token>/', views.VerifyAccount.as_view(), name='verify_account'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('logout_all/', views.LogoutAll.as_view(), name='logout_all'),
    path('active_login/', views.CheckAllActiveLogin.as_view(), name='active_login'),
    path('selected_logout/', views.SelectedLogout.as_view(), name='selected_logout'),
    path('profile/', views.ShowProfile.as_view(), name='profile'),
    path('change_password/', views.ChangePasswordView.as_view(), name='change_password'),
    path('update_profile/', views.UpdateProfileView.as_view(), name='update_profile'),
    path('password_reset_request/', views.PasswordResetRequestView.as_view(), name='password_reset_request'),
    path('password_reset/<str:uidb64>/<str:token>/', views.SetNewPasswordView.as_view(), name='password_reset'),
    path('disable_account/<str:user_spec>/', views.DisableAccount.as_view(), name='disable_account'),
    path('enable_account/<str:user_spec>/', views.EnableAccount.as_view(), name='enable_account'),
]
