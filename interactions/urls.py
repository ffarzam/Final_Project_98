from django.urls import path
from . import views

urlpatterns = [
    path('like/', views.LikeView.as_view(), name='like'),
    path('recommendation/', views.RecommendationView.as_view(), name='recommendation'),

]