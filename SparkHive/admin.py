from django.contrib import admin
from .models import Idea, Like, Comment, Follow, Notification, Skill


admin.site.register(Skill)
admin.site.register(Idea)
admin.site.register(Like)
admin.site.register(Comment)
admin.site.register(Follow)
admin.site.register(Notification)
