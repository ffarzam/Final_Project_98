from django.urls import path
from . import views


urlpatterns = [
    path('create/', views.CreateChannelAndItems.as_view(), name='create'),
    path('update/', views.UpdateChannelAndItems.as_view(), name='update'),
]


