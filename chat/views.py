from django.shortcuts import render, redirect
from django.urls import reverse
from django.conf import settings
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.utils import timezone
from urllib.parse import urlencode
import json
import base64
from itertools import chain
from datetime import datetime
import pytz
from django.http import JsonResponse
from django.core.files.storage import default_storage
from django.core.files.storage import FileSystemStorage
from django.core import files
import os


from chat.forms import ChatMessageForm
from friend.models import FriendList
from account.models import Account
from chat.models import PrivateChatRoom, RoomChatMessage, ChatMessage
from chat.utils import find_or_create_private_chat




DEBUG = False
TEMP_PROFILE_IMAGE_NAME = "temp_profile_image.png"



def private_chat_room_view(request, *args, **kwargs):
    room_id = request.GET.get("room_id")
    user = request.user
    if not user.is_authenticated:
        base_url = reverse('login')
        query_string = urlencode({'next': f"/chat/?room_id={room_id}"})
        url = f"{base_url}?{query_string}"
        return redirect(url)
    
    context = {}
    context['m_and_f'] = get_recent_chatroom_messages(user)
    context["BASE_URL"] = settings.BASE_URL
    if room_id:
        context["room_id"] = room_id
        context['debug'] = DEBUG
        context['debug_mode'] = settings.DEBUG
    return render(request, "chat/room.html", context)

        
def get_recent_chatroom_messages(user):
	"""
	sort in terms of most recent chats (users that you most recently had conversations with)
	"""
	# 1. Find all the rooms this user is a part of 
	rooms1 = PrivateChatRoom.objects.filter(user1=user, is_active=True)
	rooms2 = PrivateChatRoom.objects.filter(user2=user, is_active=True)

	# 2. merge the lists
	rooms = list(chain(rooms1, rooms2))

	# 3. find the newest msg in each room
	m_and_f = []
	for room in rooms:
		# Figure out which user is the "other user" (aka friend)
		if room.user1 == user:
			friend = room.user2
		else:
			friend = room.user1

		# confirm you are even friends (in case chat is left active somehow)
		friend_list = FriendList.objects.get(user=user)
		if not friend_list.is_mutual_friend(friend):
			chat = find_or_create_private_chat(user, friend)
			chat.is_active = False
			chat.save()
		else:	
			# find newest msg from that friend in the chat room
			try:
				message = RoomChatMessage.objects.filter(room=room, user=friend).latest("timestamp")
			except RoomChatMessage.DoesNotExist:
				# create a dummy message with dummy timestamp
				today = datetime(
					year=1950, 
					month=1, 
					day=1, 
					hour=1,
					minute=1,
					second=1,
					tzinfo=pytz.UTC
				)
				message = RoomChatMessage(
					user=friend,
					room=room,
					timestamp=today,
					content="",
				)
			m_and_f.append({
				'message': message,
				'friend': friend
			})

	return sorted(m_and_f, key=lambda x: x['message'].timestamp, reverse=True)


# Ajax call to return a private chatroom or create one if does not exist

def create_or_return_private_chat(request,pk):
    friend = FriendList.objects.get(user_id=pk)
    user = request.user
    profile = Account.objects.get(pk=friend.user.id)
    payload = {}
    form = ChatMessageForm()
    chats = ChatMessage.objects.all()
    rec_chats = ChatMessage.objects.filter(msg_sender=profile, msg_receiver=user, seen=False)
    rec_chats.update(seen=True)
    if user.is_authenticated:
        if request.method == "POST":
            form = ChatMessageForm(request.POST, request.FILES, instance=request.user)
            chat = find_or_create_private_chat(profile, user)
            if form.is_valid():
                try: 
                    chat_message = form.save(commit=False)
                    chat_message.msg_sender = user
                    chat_message.msg_receiver = profile
                    chat_message.save()
                    print("Successfully got the chat")
                    payload['response'] = "Successfully got the chat."
                    payload['chatroom_id'] = chat.id
                    return redirect("create-or-return-private-chat", pk=friend.profile.id)
                except Account.DoesNotExist:
                    payload['response'] = "Unable to start a chat with that user."
        
        context = {
			"friend": friend, "form": form, "user":user, 
            "profile":profile, "chats": chats, "num": rec_chats.count()
		}
        return render(request, "chat/room.html", context)

    
    else:
        payload['response'] = "You can't start a chat if you are not authenticated."
        return HttpResponse(json.dumps(payload), content_type="application/json")

def crochat(request):
    user = request.user
    profile = Account.objects.get(pk=user.id)
    friend_list = FriendList.objects.get(user=profile)
    friend_list.save()
    friends = friend_list.friends.all()
    context = {"user": user, "friends": friends}
    return render(request, "chat/snippets/create_or_return_private_chat.html", context)


def sentMessages(request, pk):
    user = request.user
    friend = FriendList.objects.get(user_id=pk)
    profile = Account.objects.get(pk=friend.user.id)
    data = json.loads(request.body)
    new_chat = data["msg"]
    new_chat_message = ChatMessage.objects.create(body=new_chat, msg_sender=user, msg_receiver=profile, seen=False )
    print(new_chat)
    return JsonResponse(new_chat_message.body, safe=False)

def receivedMessages(request, pk):
    user = request.user
    friend = FriendList.objects.get(user_id=pk)
    profile = Account.objects.get(pk=friend.user.id)
    arr = []
    chats = ChatMessage.objects.filter(msg_sender=profile, msg_receiver=user)
    for chat in chats:
        arr.append(chat.body)
    return JsonResponse(arr, safe=False)

def chatNotification(request):
    user = request.user
    friends = user.friends.all()
    arr = []
    for friend in friends:
        chats = ChatMessage.objects.filter(msg_sender__id=friend.user.id, msg_receiver=user, seen=False)
        arr.append(chats.count())
    return JsonResponse(arr, safe=False)
    
def save_temp_profile_image_from_base64String(imageString, user):
    INCORRECT_PADDING_EXCEPTION = "Incorrect padding"
    ACCESS = 'chat/room.html'
    try:
        url = os.path.join(ACCESS + "/" + str(user.pk))
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


    
  






    

