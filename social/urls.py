"""social URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
=======
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
>>>>>>> f98a03bb387ce676ea1fbb6a689c3a739dfe7f67
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.conf import settings
from django.conf.urls import include
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from django.urls import path

from account.views import (
    register_view,
    login_view,
    logout_view,
    account_search_view,
    like_post,
    like_video,
    upload,
    delete_post,
    delete_video,
    video_post,
    follow,
    account_view,
    profile,
    comment_post,
    comment_vid,
)

from personal.views import (
	home_screen_view,
    front_view,
)

from videochat.views import (
    room,
    getToken,
    createMember,
    getMember,
    deleteMember,
)


urlpatterns = [
    path('', home_screen_view, name='home'),
    path('welcome/', front_view, name='frontpart'),
    path('account/', include('account.urls', namespace='account')),
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path('chat/', include('chat.urls', namespace='chat')),
    path('friend/', include('friend.urls', namespace='friend')),
    path('videochat/', include('videochat.urls', namespace='videochat')),
    path('register/', register_view, name="register"),
    path('login/', login_view, name="login"),
    path('logout/', logout_view, name="logout"),
    path('room/', room, name="roommie"),
    path('get_token/', getToken, name="getToken"),

    path('create_member/', createMember, name="createMember"),
    path('get_member/', getMember, name="getMember"),
    path('delete_member/', deleteMember, name="deleteMember"),
    path('search/', account_search_view, name="search"),
    # Password reset links (ref: https://github.com/django/django/blob/master/django/contrib/auth/views.py)
    path('password_change/done/', auth_views.PasswordChangeDoneView.as_view(template_name='password_reset/password_change_done.html'), 
        name='password_change_done'),

    path('password_change/', auth_views.PasswordChangeView.as_view(template_name='password_reset/password_change.html'), 
        name='password_change'),

    path('password_reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='password_reset/password_reset_done.html'),
     name='password_reset_done'),

    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='password_reset/password_reset_complete.html'),
     name='password_reset_complete'),
    path('profile/<str:pk>', profile, name='profile'),
    path('<user_id>/', account_view, name="view"),
    path('like-post', like_post, name='like-post'),
    path('like-video', like_video, name='like-video'),
    path('comment_post', comment_post, name='comment_post'),
    path('comment_vid', comment_vid, name='comment_vid'),
    path('upload', upload, name='upload'),
    path('delete_post', delete_post, name='delete_post'),
    path('delete_video', delete_video, name='delete_video'),
    path('video_post', video_post, name='video_post'),
    path('follow', follow, name='follow'),
    


    
]

if settings.DEBUG:
   urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
   urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


urlpatterns = urlpatterns+static(settings.MEDIA_URL,
document_root=settings.MEDIA_ROOT)
