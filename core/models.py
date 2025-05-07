from django.db import models
import profile
from xmlrpc.client import Boolean
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.conf import settings
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver

#from chat.utils import find_or_create_private_chat
#from notification.models import Notification

# Create your models here.
from django.contrib.auth import get_user_model
import uuid
from datetime import datetime
from .validators import file_size
from django.contrib.auth.models import User

User = get_user_model()

# Create your models here.
class Profile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="profile_user")
    id_user = models.IntegerField()
    bio = models.TextField(blank=True)
    profileimg = models.ImageField(upload_to='profile_images', default='blank-profile-picture.png')
    personalvideo = models.FileField(upload_to='personal_videos', default='oau-anthem.mp4', validators=[file_size])
    location = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.user.username
    
class Video(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    user = models.CharField(max_length=100)
    caption=models.CharField(max_length=100) 
    video=models.FileField(upload_to="video/%y",validators=[file_size]) 
    
    def __str__(self): 
        return self.user
 

class Post(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    user = models.CharField(max_length=100)
    image = models.ImageField(upload_to='post_images')
    caption = models.TextField()
    created_at = models.DateTimeField(default=datetime.now)
    no_of_likes = models.IntegerField(default=0)

    def __str__(self):
        return self.user

class LikePost(models.Model):
    post_id = models.CharField(max_length=500)
    username = models.CharField(max_length=100)

    def __str__(self):
        return self.username

class FollowersCount(models.Model):
    follower = models.CharField(max_length=100)
    user = models.CharField(max_length=100)

    def __str__(self):
        return self.user
    
class Room(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)

class MessageManager(models.Manager):
     def by_room(self, room):
        qs = Message.objects.filter(room=room).order_by("-date_added")
        return qs 
    
class Message(models.Model):
    room = models.ForeignKey(Room, related_name='messages', on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name='messages', on_delete=models.CASCADE)
    content = models.TextField()
    date_added = models.DateTimeField(auto_now_add=True)
    
    objects = MessageManager()
    
    def __str__(self):
        return self.content
    
class Profileme(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE,related_name="profileme_user")
    pic = models.ImageField(upload_to="img", blank=True, null=True)
    friends = models.ManyToManyField('Friend', blank=True, related_name = "my_friends")
    
    def __str__(self):
        return self.user.username
    
class Friend(models.Model):
    profileme = models.OneToOneField(Profileme, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.profileme.user.username

class ChatMessage(models.Model):
    body = models.TextField()
    msg_sender = models.ForeignKey(Profileme, on_delete=models.CASCADE, related_name="msg_sender")
    msg_receiver = models.ForeignKey(Profileme, on_delete=models.CASCADE, related_name="msg_receiver")
    seen = models.BooleanField(default=False)
    
    def __str__(self):
        return self.body