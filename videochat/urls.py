from django.urls import path
from . import views

app_name = 'videochat'


urlpatterns = [
    path('', views.lobby, name="lobby"),
   
]