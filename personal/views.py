from django.shortcuts import render
from django.conf import settings
from account.models import Account, Video, Post, \
LikePost, FollowersCount, Profile
from django.conf import settings
from django.core import files
from itertools import chain
import random 
from django.contrib.auth.decorators import login_required



@login_required(login_url='login')
def home_screen_view(request, *args, **kwargs):
    user_object = Account.objects.get(username=request.user.username)
    
    # Automatically create Profile if it doesn't exist
    user_profile, created = Profile.objects.get_or_create(user=user_object, defaults={'id_user': user_object.id})
    
    user_following_list = []
    feed = []
    feed_1 = []

    user_following = FollowersCount.objects.filter(follower=request.user.username)

    for users in user_following:
        user_following_list.append(users.user)

    for usernames in user_following_list:
        feed_videos = Video.objects.all()
        feed_lists = Post.objects.filter(user=usernames)
        feed_person = Post.objects.filter(user=user_profile)
        feed.append(feed_lists)
        feed_1.append(feed_videos)
        feed.append(feed_person)

    feed_list = list(chain(*feed))
    feed_list1 = list(chain(*feed_1))

    # user suggestion starts
    all_users = Account.objects.all()
    user_following_all = []

    for user in user_following:
        user_list = Account.objects.get(username=user.user)
        user_following_all.append(user_list)

    new_suggestions_list = [
        x for x in list(all_users)
        if x not in user_following_all
    ]
    current_user = Account.objects.filter(username=request.user.username)
    final_suggestions_list = [
        x for x in new_suggestions_list
        if x not in current_user
    ]
    random.shuffle(final_suggestions_list)

    username_profile = []
    username_profile_list = []

    for users in final_suggestions_list:
        username_profile.append(users.id)

    for ids in username_profile:
        profile_lists = Profile.objects.filter(id_user=ids)
        username_profile_list.append(profile_lists)

    suggestions_username_profile_list = list(chain(*username_profile_list))

    return render(request, 'personal/home.html', {
        'user_profile': user_profile,
        'videofeed': feed_list1,
        'posts': feed_list,
        'suggestions_username_profile_list': suggestions_username_profile_list[:4]
    })


@login_required(login_url='login')
def front_view(request):
    return render(request, 'personal/front.html')





