from django.contrib import admin
from .models import Post, Profile, LikePost,\
FollowersCount, Video, Room, Profileme, Friend, ChatMessage

# Register your models here.
admin.site.register(Post)
admin.site.register(Profile)
admin.site.register(LikePost)
admin.site.register(FollowersCount)
admin.site.register(Video)
admin.site.register(Room)
admin.site.register(Profileme)
admin.site.register(Friend)
admin.site.register(ChatMessage)


  
