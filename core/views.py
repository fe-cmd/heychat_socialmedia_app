from django.shortcuts import render, redirect
from django.contrib.auth.models import auth
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .forms import ChatMessageForm
from .models import (
    Profile, Post, LikePost, FollowersCount, Video, Room,
    Message, Profileme, ChatMessage, Friend
)

import json
from itertools import chain
import random

User = get_user_model()


@login_required(login_url='signin')
def index(request):
    user_profile = Profile.objects.get(user=request.user)

    following = FollowersCount.objects.filter(follower=request.user.username)
    following_usernames = [f.user for f in following]

    posts = list(chain(*[Post.objects.filter(user=username) for username in following_usernames]))
    videos = Video.objects.all()

    # Suggestions
    all_users = User.objects.exclude(username=request.user.username)
    following_users = User.objects.filter(username__in=following_usernames)
    suggestions = list(set(all_users) - set(following_users))
    random.shuffle(suggestions)

    suggested_profiles = list(chain(*[Profile.objects.filter(user=user) for user in suggestions]))[:4]

    return render(request, 'index.html', {
        'user_profile': user_profile,
        'posts': posts,
        'videofeed': videos,
        'suggestions_username_profile_list': suggested_profiles
    })


def signup(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip().lower()
        email = request.POST.get('email', '').strip().lower()
        password = request.POST.get('password')
        password2 = request.POST.get('password2')

        # Check password match
        if password != password2:
            messages.info(request, 'Passwords do not match')
            return redirect('signup')

        # Check if user already exists
        if User.objects.filter(username=username).exists():
            messages.info(request, 'Username taken')
            return redirect('signup')
        if User.objects.filter(email=email).exists():
            messages.info(request, 'Email taken')
            return redirect('signup')

        # Create user safely
        user = User.objects.create_user(username=username, email=email, password=password)
        user.save()  # Not strictly necessary after create_user, but safe

        # Create profile
        Profile.objects.create(user=user, id_user=user.id)

        # Auto-login after signup
        auth.login(request, user)
        return redirect('settings')

    return render(request, 'signup.html')

def signin(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip().lower()
        password = request.POST.get('password')

        user = auth.authenticate(username=username, password=password)

        if user is not None:
            auth.login(request, user)
            return redirect('/')
        else:
            messages.info(request, 'Invalid credentials')
            return redirect('signin')

    return render(request, 'signin.html')

@login_required(login_url='signin')
def logout(request):
    auth.logout(request)
    return redirect('signin')


@login_required(login_url='signin')
def settings(request):
    profile = Profile.objects.get(user=request.user)

    if request.method == 'POST':
        profile.profileimg = request.FILES.get('image', profile.profileimg)
        profile.personalvideo = request.FILES.get('video', profile.personalvideo)
        profile.bio = request.POST.get('bio', profile.bio)
        profile.location = request.POST.get('location', profile.location)
        profile.save()
        return redirect('settings')

    return render(request, 'setting.html', {'user_profile': profile})


@login_required(login_url='signin')
def upload(request):
    if request.method == 'POST':
        Post.objects.create(
            user=request.user.username,
            image=request.FILES.get('image_upload'),
            caption=request.POST['caption']
        )
    return redirect('/')


@login_required(login_url='signin')
def video_post(request):
    if request.method == 'POST':
        Video.objects.create(
            user=request.user.username,
            video=request.FILES.get('video_upload'),
            caption=request.POST['caption']
        )
    return redirect('/')


@login_required(login_url='signin')
def like_post(request):
    post_id = request.GET.get('post_id')
    post = Post.objects.get(id=post_id)
    username = request.user.username

    like = LikePost.objects.filter(post_id=post_id, username=username).first()

    if like:
        like.delete()
        post.no_of_likes -= 1
    else:
        LikePost.objects.create(post_id=post_id, username=username)
        post.no_of_likes += 1

    post.save()
    return redirect('/')


@login_required(login_url='signin')
def profile(request, pk):
    target_user = User.objects.get(username=pk)
    profile = Profile.objects.get(user=target_user)
    posts = Post.objects.filter(user=pk)
    following = FollowersCount.objects.filter(follower=request.user.username, user=pk)

    context = {
        'user_object': target_user,
        'user_profile': profile,
        'user_posts': posts,
        'user_post_length': posts.count(),
        'button_text': 'Unfollow' if following else 'Follow',
        'user_followers': FollowersCount.objects.filter(user=pk).count(),
        'user_following': FollowersCount.objects.filter(follower=pk).count(),
    }
    return render(request, 'profile.html', context)


@login_required(login_url='signin')
def follow(request):
    if request.method == 'POST':
        follower = request.POST['follower']
        user = request.POST['user']

        follow_entry = FollowersCount.objects.filter(follower=follower, user=user).first()

        if follow_entry:
            follow_entry.delete()
        else:
            FollowersCount.objects.create(follower=follower, user=user)

        return redirect('/profile/' + user)
    return redirect('/')


@login_required(login_url='signin')
def search(request):
    profile = Profile.objects.get(user=request.user)

    if request.method == 'POST':
        username = request.POST['username']
        users = User.objects.filter(username__icontains=username)

        profiles = list(chain(*[Profile.objects.filter(user=user) for user in users]))
        return render(request, 'search.html', {'user_profile': profile, 'username_profile_list': profiles})

    return redirect('/')


@login_required(login_url='signin')
def delete_post(request):
    Post.objects.filter(id=request.GET.get('post_id'), user=request.user.username).delete()
    return redirect('index')


@login_required(login_url='signin')
def frontpage(request):
    return render(request, 'base.html', {"user_profile": Profile.objects.get(user=request.user)})


@login_required(login_url='signin')
def homes(request):
    return render(request, 'homes.html', {
        'homes': Room.objects.all(),
        'user_profile': Profile.objects.get(user=request.user)
    })


@login_required(login_url='signin')
def home(request, slug):
    room = Room.objects.get(slug=slug)
    messages = Message.objects.filter(room=room)[:25]
    return render(request, 'home.html', {
        'home': room,
        'messages': messages,
        'user_profile': Profile.objects.get(user=request.user)
    })


@login_required(login_url='signin')
def begin(request):
    user = request.user.profileme
    return render(request, "begin.html", {"user": user, "friends": user.friends.all()})


@login_required(login_url='signin')
def detail(request, pk):
    friend = Friend.objects.get(profileme_id=pk)
    user = request.user.profileme
    profile = friend.profileme
    chats = ChatMessage.objects.all()
    unread = ChatMessage.objects.filter(msg_sender=profile, msg_receiver=user, seen=False)
    unread.update(seen=True)

    if request.method == "POST":
        form = ChatMessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.msg_sender = user
            message.msg_receiver = profile
            message.save()
            return redirect("detail", pk=profile.id)
    else:
        form = ChatMessageForm()

    return render(request, "detail.html", {
        "friend": friend,
        "form": form,
        "user": user,
        "profile": profile,
        "chats": chats,
        "num": unread.count()
    })


@login_required(login_url='signin')
def sentMessages(request, pk):
    user = request.user.profileme
    profile = Friend.objects.get(profileme_id=pk).profileme
    data = json.loads(request.body)
    new_msg = ChatMessage.objects.create(
        body=data["msg"],
        msg_sender=user,
        msg_receiver=profile,
        seen=False
    )
    return JsonResponse(new_msg.body, safe=False)


@login_required(login_url='signin')
def receivedMessages(request, pk):
    user = request.user.profileme
    profile = Friend.objects.get(profileme_id=pk).profileme
    chats = ChatMessage.objects.filter(msg_sender=profile, msg_receiver=user)
    return JsonResponse([chat.body for chat in chats], safe=False)


@login_required(login_url='signin')
def chatNotification(request):
    user = request.user.profileme
    counts = [
        ChatMessage.objects.filter(msg_sender__id=friend.profileme.id, msg_receiver=user, seen=False).count()
        for friend in user.friends.all()
    ]
    return JsonResponse(counts, safe=False)
