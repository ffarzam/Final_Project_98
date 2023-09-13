from django.urls import path
from . import views


urlpatterns = [
    path('status/', views.Status.as_view(), name='status'),
    path('login/', views.UserLogin.as_view(), name='login'),
    path('login/refresh/', views.RefreshToken.as_view(), name='token_refresh'),
    path('register/', views.UserRegister.as_view(), name='register'),
    path('logout/', views.LogoutView.as_view(), name='logout'),

]


