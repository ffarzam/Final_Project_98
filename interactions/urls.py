from django.urls import path
from . import views

app_name = "interactions"
urlpatterns = [
    path('like/', views.LikeView.as_view(), name='like'),
    path('recommendation/', views.RecommendationView.as_view(), name='recommendation'),
    path('create_comment/', views.CreateCommentView.as_view(), name='create_comment'),
    path('comments_list/<int:channel_id>/<int:item_id>', views.CommentListView.as_view(), name='comments_list'),
    path('user_liked_episode_list/', views.UserEpisodeLikeList.as_view(), name='user_liked_episode_list'),
    path('user_liked_news_list/', views.UserNewsLikeList.as_view(), name='user_liked_news_list'),
    path('bookmark_channel/', views.BookmarkChannel.as_view(), name='bookmark_channel'),
    path('user_bookmarked_channel_list/', views.UserBookmarkChannelList.as_view(), name='user_bookmarked_channel_list'),
    path('bookmark_item/', views.BookmarkItem.as_view(), name='bookmark_item'),
    path('user_bookmarked_episode_list/', views.UserBookmarkEpisodeList.as_view(), name='user_bookmarked_episode_list'),
    path('user_bookmarked_news_list/', views.UserBookmarkNewsList.as_view(), name='user_bookmarked_news_list'),
]