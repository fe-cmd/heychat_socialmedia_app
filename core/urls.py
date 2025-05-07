from django.urls import path 
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('settings', views.settings, name='settings'),
    path('upload', views.upload, name='upload'),
    path('delete_post', views.delete_post, name='delete_post'),
    path('video_post', views.video_post, name='video_post'),
    path('follow', views.follow, name='follow'),
    path('search', views.search, name='search'),
    path('frontpage', views.frontpage, name='frontpage'),
    path('homes', views.homes, name='homes'),
    path('<slug:slug>/', views.home, name='home'),
    path('profile/<str:pk>', views.profile, name='profile'),
    path('like-post', views.like_post, name='like-post'),
    path('signup', views.signup, name='signup'),
    path('signin', views.signin, name='signin'),
    path('logout', views.logout, name='logout'),
    #chats
    path('begin', views.begin, name= "begin"),
    path('friend/<str:pk>', views.detail, name="detail"),
    path('sent_msg/<str:pk>', views.sentMessages, name = "sent_msg"),
    path('rec_msg/<str:pk>', views.receivedMessages, name = "rec_msg"),
    path('notification', views.chatNotification, name = "notification"),
]