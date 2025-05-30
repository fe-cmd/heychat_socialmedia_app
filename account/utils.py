from django.core.serializers.python import Serializer
from datetime import datetime
from django.contrib.humanize.templatetags.humanize import naturalday
from account.constants import *


def calculate_timestamp(timestamp):
    """
	1. Today or yesterday:
		- EX: 'today at 10:56 AM'
		- EX: 'yesterday at 5:19 PM'
	2. other:
		- EX: 05/06/2020
		- EX: 12/28/2020
	"""
    ts = ""
    # Today or yesterday
    if (naturalday(timestamp) == "today") or (naturalday(timestamp) == "yesterday"):
     str_time = datetime.strftime(timestamp, "%I:%M %p")
     str_time = str_time.strip("0")
     ts = f"{naturalday(timestamp)} at {str_time}"
     # other days
    else:
        str_time = datetime.strftime(timestamp, "%m/%d/%Y")
        ts = f"{str_time}"
    return str(ts)
    
        
	  


class LazyAccountEncoder(Serializer):
    def get_dump_object(self, obj):
        dump_object = {}
        dump_object.update({'id': str(obj.id)})
        dump_object.update({'msg_type': MSG_TYPE_MESSAGE})
        dump_object.update({'msg_id': str(obj.id)})
        dump_object.update({'email': str(obj.email)})
        dump_object.update({'user_id': str(obj.user.id)})
        dump_object.update({'username': str(obj.username)})
        dump_object.update({'message': str(obj.content)})
        dump_object.update({'profile_image': str(obj.profile_image.url)})
        dump_object.update({'natural_timestamp': calculate_timestamp(obj.timestamp)})
        return dump_object
