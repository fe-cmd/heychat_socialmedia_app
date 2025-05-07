from socket import fromshare
from django import forms
from django.forms import ModelForm
from .models import ChatMessage


class ChatMessageForm(ModelForm):
    body = forms.CharField(widget=forms.Textarea(attrs={"class":"forms", "id":"myform", "rows":5, "placeholder": "Type message here"}))
    class Meta:
        model = ChatMessage
        fields = ["body",]
