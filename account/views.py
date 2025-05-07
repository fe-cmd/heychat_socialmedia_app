from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponse
from django.contrib.auth import login, authenticate, logout
from django.conf import settings
from django.contrib.auth.decorators import login_required

from django.core.files.storage import default_storage
from django.core.files.storage import FileSystemStorage
import os
import cv2
import json
import base64
import requests
from django.core import files
from itertools import chain
import random 

from videochat.models import RoomMember
from account.forms import RegistrationForm, AccountAuthenticationForm, AccountUpdateForm, CommentForm, CommentForms
from account.models import Account, Video, Post, \
LikePost, FollowersCount, Profile, Commentpic, Commentvid
from friend.utils import get_friend_request_or_false
from friend.friend_request_status import FriendRequestStatus
from friend.models import FriendList, FriendRequest


TEMP_PROFILE_IMAGE_NAME = "temp_profile_image.png"



# This is basically almost exactly the same as friends/friend_list_view
@login_required(login_url='login')
def account_search_view(request):
	if request.method == "POST":
		search_query = request.POST["q"]
		if len(search_query) > 0:
			search_results = Account.objects.filter(username__icontains=search_query)
			user = request.user
			accounts = [] # [(account1, True), (account2, False), ...]
			if user.is_authenticated:
				# get the authenticated users friend list
				auth_user_friend_list = FriendList.objects.get(user=user)
				for account in search_results:
					accounts.append((account, auth_user_friend_list.is_mutual_friend(account)))
     			
	return render(request, "account/search_results.html", {"accounts": accounts})



def register_view(request, *args, **kwargs):
    user = request.user
    if user.is_authenticated:
        return HttpResponse("You are already authenticated as " + str(user.email))
    context = {}
    if request.POST:
        form = RegistrationForm(request.POST)
        if form.is_valid():
           form.save()
           email = form.cleaned_data.get('email').lower()
           raw_password = form.cleaned_data.get('password1')
           username = form.cleaned_data.get('username')
           account = authenticate(email=email, password=raw_password)
           login(request, account)
           #create a Profile object for the new user
           user_model = Account.objects.get(username=username)
           new_profile = Profile.objects.create(user=user_model, id_user=user_model.id)
           new_profile.save()
           destination = kwargs.get("next")
           if destination:
               return redirect(destination)
           return redirect('front')
        else:
           context['registration_form'] = form
           
    else:
        form = RegistrationForm()
        context['registration_form'] = form
    return render(request, 'account/register.html', context)

        
@login_required(login_url='login')
def logout_view(request):
	logout(request)
	return redirect("home")


def login_view(request, *args, **kwargs):
	context = {}

	user = request.user
	if user.is_authenticated: 
		return redirect("front")

	if request.POST:
		form = AccountAuthenticationForm(request.POST)
		if form.is_valid():
			email = request.POST['email']
			password = request.POST['password']
			user = authenticate(email=email, password=password)

			if user:
				login(request, user)
				return redirect("front")

	else:
		form = AccountAuthenticationForm()

	context['login_form'] = form

	return render(request, "account/login.html", context)

@login_required(login_url='login')
def get_redirect_if_exists(request):
	redirect = None
	if request.GET:
		if request.GET.get("next"):
			redirect = str(request.GET.get("next"))
	return redirect


@login_required(login_url='login')
def profile(request, pk):
    user_object = Account.objects.get(username=pk)
    user_profile = Profile.objects.get(user=user_object)
        
    user_posts = Post.objects.filter(user=pk)
    user_post_length = len(user_posts)

    follower = request.user.username
    user = pk

    if FollowersCount.objects.filter(follower=follower, user=user).first():
        button_text = 'Unfollow'
    else:
        button_text = 'Follow'

    user_followers = len(FollowersCount.objects.filter(user=pk))
    user_following = len(FollowersCount.objects.filter(follower=pk))

    context = {
        'user_object': user_object,
        'user_profile': user_profile,
        'user_posts': user_posts,
        'user_post_length': user_post_length,
        'button_text': button_text,
        'user_followers': user_followers,
        'user_following': user_following,
    }
    return render(request, 'account/profile.html', context)




def account_view(request, *args, **kwargs):
	"""
	- Logic here is kind of tricky
		is_self
		is_friend
			-1: NO_REQUEST_SENT
			0: THEM_SENT_TO_YOU
			1: YOU_SENT_TO_THEM
	"""
	context = {}
	user_id = kwargs.get("user_id")
	try:
		account = Account.objects.get(pk=user_id)
	except:
		return HttpResponse("Something went wrong.")
	if account:
		context['id'] = account.id
		context['username'] = account.username
		context['email'] = account.email
		context['profile_image'] = account.profile_image.url
		context['hide_email'] = account.hide_email

		try:
      
			friend_list = FriendList.objects.get(user=account)
		except FriendList.DoesNotExist:
			friend_list = FriendList(user=account)
			friend_list.save()
		friends = friend_list.friends.all()
		context['friends'] = friends
	
		# Define template variables
		is_self = True
		is_friend = False
		request_sent = FriendRequestStatus.NO_REQUEST_SENT.value # range: ENUM -> friend/friend_request_status.FriendRequestStatus
		friend_requests = None
		user = request.user
		if user.is_authenticated and user != account:
			is_self = False
			if friends.filter(pk=user.id):
				is_friend = True
			else:
				is_friend = False
				# CASE1: Request has been sent from THEM to YOU: FriendRequestStatus.THEM_SENT_TO_YOU
				if get_friend_request_or_false(sender=account, receiver=user) != False:
					request_sent = FriendRequestStatus.THEM_SENT_TO_YOU.value
					context['pending_friend_request_id'] = get_friend_request_or_false(sender=account, receiver=user).id
				# CASE2: Request has been sent from YOU to THEM: FriendRequestStatus.YOU_SENT_TO_THEM
				elif get_friend_request_or_false(sender=user, receiver=account) != False:
					request_sent = FriendRequestStatus.YOU_SENT_TO_THEM.value
				# CASE3: No request sent from YOU or THEM: FriendRequestStatus.NO_REQUEST_SENT
				else:
					request_sent = FriendRequestStatus.NO_REQUEST_SENT.value
		
		elif not user.is_authenticated:
			is_self = False
		else:
			try:
				friend_requests = FriendRequest.objects.filter(receiver=user, is_active=True)
			except:
				pass
			
		# Set the template variables to the values
		context['is_self'] = is_self
		context['is_friend'] = is_friend
		context['request_sent'] = request_sent
		context['friend_requests'] = friend_requests
		context['BASE_URL'] = settings.BASE_URL
		return render(request, "account/account.html", context)



def save_temp_profile_image_from_base64String(imageString, user):
	INCORRECT_PADDING_EXCEPTION = "Incorrect padding"
	try:
		if not os.path.exists(settings.TEMP):
			os.mkdir(settings.TEMP)
		if not os.path.exists(settings.TEMP + "/" + str(user.pk)):
			os.mkdir(settings.TEMP + "/" + str(user.pk))
		url = os.path.join(settings.TEMP + "/" + str(user.pk),TEMP_PROFILE_IMAGE_NAME)
		storage = FileSystemStorage(location=url)
		image = base64.b64decode(imageString)
		with storage.open('', 'wb+') as destination:
			destination.write(image)
			destination.close()
		return url
	except Exception as e:
		print("exception: " + str(e))
		# workaround for an issue I found
		if str(e) == INCORRECT_PADDING_EXCEPTION:
			imageString += "=" * ((4 - len(imageString) % 4) % 4)
			return save_temp_profile_image_from_base64String(imageString, user)
	return None


def crop_image(request, *args, **kwargs):
	payload = {}
	user = request.user
	if request.POST and user.is_authenticated:
		try:
			imageString = request.POST.get("image")
			url = save_temp_profile_image_from_base64String(imageString, user)
			img = cv2.imread(url)

			cropX = int(float(str(request.POST.get("cropX"))))
			cropY = int(float(str(request.POST.get("cropY"))))
			cropWidth = int(float(str(request.POST.get("cropWidth"))))
			cropHeight = int(float(str(request.POST.get("cropHeight"))))
			if cropX < 0:
				cropX = 0
			if cropY < 0: # There is a bug with cropperjs. y can be negative.
				cropY = 0
			crop_img = img[cropY:cropY+cropHeight, cropX:cropX+cropWidth]

			cv2.imwrite(url, crop_img)

			# delete the old image
			user.profile_image.delete()

			# Save the cropped image to user model
			user.profile_image.save("profile_image.png", files.File(open(url, 'rb')))
			user.save()

			payload['result'] = "success"
			payload['cropped_profile_image'] = user.profile_image.url

			# delete temp file
			os.remove(url)
			
		except Exception as e:
			print("exception: " + str(e))
			payload['result'] = "error"
			payload['exception'] = str(e)
	return HttpResponse(json.dumps(payload), content_type="application/json")


def edit_account_view(request, *args, **kwargs):
	if not request.user.is_authenticated:
		return redirect("login")
	user_id = kwargs.get("user_id")
	account = Account.objects.get(pk=user_id)
	if account.pk != request.user.pk:
		return HttpResponse("You cannot edit someone elses profile.")
	context = {}
	if request.POST:
		form = AccountUpdateForm(request.POST, request.FILES, instance=request.user)
		if form.is_valid():
			form.save()
			return redirect("account:view", user_id=account.pk)
		else:
			form = AccountUpdateForm(request.POST, instance=request.user,
				initial={
					"id": account.pk,
					"email": account.email, 
					"username": account.username,
					"profile_image": account.profile_image,
					"hide_email": account.hide_email,
				}
			)
			context['form'] = form
	else:
		form = AccountUpdateForm(
			initial={
					"id": account.pk,
					"email": account.email, 
					"username": account.username,
					"profile_image": account.profile_image,
					"hide_email": account.hide_email,
				}
			)
		context['form'] = form
	context['DATA_UPLOAD_MAX_MEMORY_SIZE'] = settings.DATA_UPLOAD_MAX_MEMORY_SIZE
	return render(request, "account/edit_account.html", context)

@login_required(login_url='login')
def video_post(request): 
   if request.method == 'POST':
      user = request.user.username
      video = request.FILES.get('video_upload')
      caption = request.POST['caption']
        
      new_post = Video.objects.create(user=user, video=video, caption=caption)
      new_post.save()

      return redirect('/')

   else: 
      return redirect('/') 
  

@login_required(login_url='login')
def upload(request):
    
    if request.method == 'POST':
        user = request.user.username
        image = request.FILES.get('image_upload')
        caption = request.POST['caption']
        
        new_post = Post.objects.create(user=user, image=image, caption=caption)
        new_post.save()

        return redirect('/')
    else:
        return redirect('/')


@login_required(login_url='login')
def like_post(request):
    
    
    username = request.user.username
    post_id = request.GET.get('post_id')

    post = Post.objects.get(id=post_id)

    like_filter = LikePost.objects.filter(post_id=post_id, username=username).first()

    if like_filter == None:
        new_like = LikePost.objects.create(post_id=post_id, username=username)
        new_like.save()
        post.no_of_likes = post.no_of_likes+1
        post.save()
        return redirect('/')
    else:
        like_filter.delete()
        post.no_of_likes = post.no_of_likes-1
        post.save()
        return redirect('/')
    
@login_required(login_url='login')
def like_video(request):
 
    username = request.user.username

    vidop = Video.objects.get(user=username)

    like_filter = LikePost.objects.filter(username=username).order_by('-id')

    if like_filter == None:
        new_like = LikePost.objects.create(username=username)
        new_like.save()
        vidop.no_of_likes = vidop.no_of_likes+1
        vidop.save()
        return redirect('/')
    else:
        like_filter.delete()
        vidop.no_of_likes = vidop.no_of_likes-1
        vidop.save()
        return redirect('/')

@login_required(login_url='login')
def follow(request):
    if request.method == 'POST':
        follower = request.POST['follower']
        user = request.POST['user']

        if FollowersCount.objects.filter(follower=follower, user=user).first():
            delete_follower = FollowersCount.objects.get(follower=follower, user=user)
            delete_follower.delete()
            return redirect('/profile/'+user)
        else:
            new_follower = FollowersCount.objects.create(follower=follower, user=user)
            new_follower.save()
            return redirect('/profile/'+user)
    else:
        return redirect('/')
    

@login_required(login_url='login')
def delete_post(request):
    post_id = request.GET.get('post_id')
    post = Post.objects.get(id=post_id, user=request.user.username).delete()
    return redirect('/')

@login_required(login_url='login')
def delete_video(request):
    username = request.user.username
    vidop = Video.objects.get(user=username).delete()
    return redirect('/')


@login_required(login_url='login')
def comment_post(request):
    username = request.user.username
    comments = Commentpic.objects.filter(user=username, reply=None).order_by('-id')
    
    
    if request.method == 'POST':
        comment_form = CommentForm(request.POST or None)
        if comment_form.is_valid():
            content = request.POST.get('content')
            reply_id = request.POST.get('comment_id')
            comment_qs = None
            if reply_id:
                comment_qs = Commentpic.objects.get(post_id=reply_id)
            comment = Commentpic.objects.create(user=username, content=content, reply=comment_qs)
            comment.save()
            return redirect('comment_post')
    else:
        comment_form = CommentForm()
    
    context = {
        'comments': comments, 
        'comment_form': comment_form
        }
        
    
    return render(request, 'account/comment.html', context)


@login_required(login_url='login')
def comment_vid(request):
    username = request.user.username
    comments = Commentvid.objects.filter(user=username, reply=None).order_by('-id')
    
    
    if request.method == 'POST':
        comment_forms = CommentForms(request.POST or None)
        if comment_forms.is_valid():
            content = request.POST.get('content')
            reply_id = request.POST.get('comment_id')
            comment_qs = None
            if reply_id:
                comment_qs = Commentvid.objects.get(post_id=reply_id)
            comment = Commentvid.objects.create(user=username, content=content, reply=comment_qs)
            comment.save()
            return redirect('comment_vid')
    else:
        comment_forms = CommentForms()
    
    context = {
        'comments': comments, 
        'comment_forms': comment_forms
        }
        
    
    
    return render(request, 'account/commentvid.html', context)




















