from django.urls import path

from chat.views import(
	private_chat_room_view,
	create_or_return_private_chat,
    crochat,
    sentMessages,
    receivedMessages,
    chatNotification,
)

app_name = 'chat'

urlpatterns = [
	path('', private_chat_room_view, name='private-chat-room'),
	path('friend/<str:pk>/', create_or_return_private_chat, name='create_or_return_private_chat'),
    path('friendlist/', crochat, name= 'crochat'),
    path('sent_msg/<str:pk>/', sentMessages, name = 'sent_msg'),
    path('rec_msg/<str:pk>/', receivedMessages, name = 'rec_msg'),
    path('notification/', chatNotification, name = 'notification'),



]