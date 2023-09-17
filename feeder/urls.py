from django.urls import path
from . import views

urlpatterns = [
    path('create/', views.CreateChannelAndItems.as_view(), name='create'),
    path('update/', views.UpdateChannelAndItems.as_view(), name='update'),
    path('channel_list/', views.ChannelList.as_view(), name='channel_list'),
    path('items_list/<int:channel_id>', views.ItemsList.as_view(), name='items_list'),
    path('get_channel/<int:pk>', views.GetChannel.as_view(), name='get_channel'),
    path('get_item/<int:channel_id>/<int:item_id>', views.GetItem.as_view(), name='get_item'),
]
