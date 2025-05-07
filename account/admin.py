from xml.etree.ElementTree import Comment
from django.contrib import admin
from account.models import Account, FollowersCount, LikePost, Post, Video, Profile, Commentpic, Commentvid
from django.contrib.auth.admin import UserAdmin

class AccountAdmin(UserAdmin):
    list_display = ('email','username','date_joined', 'last_login', 'is_admin','is_staff')
    search_fields = ('email','username',)
    readonly_fields=('id', 'date_joined', 'last_login')
    
    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()
	

admin.site.register(Account, AccountAdmin)
admin.site.register(Commentpic)
admin.site.register(Commentvid)
admin.site.register(FollowersCount)
admin.site.register(LikePost)
admin.site.register(Post)
admin.site.register(Video)
admin.site.register(Profile)




