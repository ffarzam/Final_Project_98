from django.urls import path
from . import views

urlpatterns = [
    path('create/', views.CreateChannelAndItems.as_view(), name='create'),
    path('update/', views.UpdateChannelAndItems.as_view(), name='update'),
    path('channel_list/', views.ChannelList.as_view(), name='channel_list'),
]
