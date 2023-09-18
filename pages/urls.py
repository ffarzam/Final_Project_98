from django.urls import path
from . import views


urlpatterns = [
    path('status/', views.Status.as_view(), name='status'),
    path('visitors_count/', views.VisitorsCount.as_view(), name='visitors_count'),

]


