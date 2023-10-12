from django.urls import path
from . import views

app_name = "feeder"
urlpatterns = [
    path('update/', views.UpdateChannelAndItems.as_view(), name='update'),
    path('channel_list/', views.ChannelList.as_view(), name='channel_list'),
    path('items_list/<int:channel_id>', views.ItemsList.as_view(), name='items_list'),
    path('get_channel/<int:pk>', views.GetChannel.as_view(), name='get_channel'),
    path('get_item/<int:channel_id>/<int:item_id>', views.GetItem.as_view(), name='get_item'),
    path('search/', views.SearchView.as_view(), name='search'),
    path('save_seconds/', views.SaveListenEpisodeSeconds.as_view(), name='save_seconds'),
]
