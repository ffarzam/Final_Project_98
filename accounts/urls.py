from django.urls import path
from . import views


urlpatterns = [
    path('login/', views.UserLogin.as_view(), name='login'),
    path('login/refresh/', views.RefreshToken.as_view(), name='token_refresh'),
    path('register/', views.UserRegister.as_view(), name='register'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('active_login/', views.CheckAllActiveLogin.as_view(), name='active_login'),
    path('selected_logout/', views.SelectedLogout.as_view(), name='selected_logout'),

]


