from django import forms
from django.forms import CharField, ModelForm
from chat.models import ChatMessage


class ChatMessageForm(ModelForm):
    body = forms.CharField(widget=forms.Textarea(attrs={"class":"forms", "rows":3, "placeholder": "Type message here"}))
    class Meta:
        model = ChatMessage
        fields = ["body", "image", "video", "file"]
        
    def save(self, commit=True):
        message = super(ChatMessageForm, self).save(commit=False)
        message.body = self.cleaned_data['body']
        message.video = self.cleaned_data['video']
        message.image = self.cleaned_data['image']
        message.file = self.cleaned_data['file']
        if commit:
            message.save()
        return message


	