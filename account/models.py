from pyexpat import model
from django.db import models
from django.core.files.storage import FileSystemStorage
from django.contrib.auth.models import (AbstractBaseUser, BaseUserManager)

import profile
from xmlrpc.client import Boolean
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.contenttypes.models import ContentType
import os
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail

import uuid
from django.utils.translation import gettext_lazy as _
from datetime import datetime
from .validators import file_size

from friend.models import FriendList



class MyAccountManager(BaseUserManager):
    def create_user(self, email, username, password=None):
        if not username:
            raise ValueError('Users must have a username')

        if not email:
            raise ValueError('You must provide an email address')

        user = self.model(
			email=self.normalize_email(email),
			username=username,
		)
        
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, username, password):
    
        user = self.create_user(
			email=self.normalize_email(email),
			password=password,
			username=username,
		)
        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user

class Account(AbstractBaseUser):
    email = models.EmailField(verbose_name='email', max_length=60, unique=True)
    username = models.CharField(max_length=30, unique=True)
    bio = models.TextField(blank=True)
    date_joined = models.DateTimeField(verbose_name='date joined', auto_now_add=True)
    last_login = models.DateTimeField(verbose_name='last login', auto_now=True)
    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    profile_image = models.ImageField(max_length=255, upload_to='profile_images', default='blank-profile-picture.png')
    hide_email = models.BooleanField(default=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    objects = MyAccountManager()
    
    
    def __str__(self):
        return self.username
    
    def has_perm(self, perm, obj=None):
        return self.is_admin
    
    def has_module_perms(self, app_label):
        return True
    
    def email_user(self, subject, message):
        send_mail(
            subject,
            message,
            'l@1.com',
            [self.email],
            fail_silently=False,
        )
        
    
@receiver(post_save, sender=Account)
def user_save(sender, instance, **kwargs):
    FriendList.objects.get_or_create(user=instance)
    
class Profile(models.Model):
    user = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='profile')
    id_user = models.IntegerField()
    bio = models.TextField(blank=True)
    profileimg = models.ImageField(upload_to='profile_images', default='default_profile_image.png')
    personalvideo = models.FileField(upload_to='personal_videos', default='oau-anthem.mp4', validators=[file_size])
    location = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.user.username
    
class Video(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    user = models.CharField(max_length=100)
    caption=models.CharField(max_length=100) 
    video=models.FileField(upload_to="video/%y",validators=[file_size]) 
    created_at = models.DateTimeField(default=datetime.now)
    no_of_likes = models.IntegerField(default=0)

    
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
    username =models.CharField(max_length=100)

    def __str__(self):
        return self.username

class FollowersCount(models.Model):
    follower = models.CharField(max_length=100)
    user = models.CharField(max_length=100)

    def __str__(self):
        return self.user
    
class Commentpic(models.Model):
    post_id = models.CharField(max_length=500)
    user = models.CharField(max_length=100)
    reply = models.ForeignKey('Commentpic', null=True, related_name='replies', on_delete=models.CASCADE)
    content = models.TextField(max_length=160)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.user
    

class Commentvid(models.Model):
    post_id = models.CharField(max_length=500)
    user = models.CharField(max_length=100)
    reply = models.ForeignKey('Commentvid', null=True, related_name='replies', on_delete=models.CASCADE)
    content = models.TextField(max_length=160)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.user
    
    