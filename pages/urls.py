from django.urls import path
from . import views

app_name = "pages"
urlpatterns = [
    path('status/', views.Status.as_view(), name='status'),
]


