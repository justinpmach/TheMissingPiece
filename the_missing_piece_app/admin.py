from django.contrib import admin
from the_missing_piece_app.models import User, FriendsList, Story, Comment

# Register your models here.
admin.site.register(User)
admin.site.register(FriendsList)
admin.site.register(Story)
admin.site.register(Comment)