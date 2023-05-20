from django.contrib import admin
from network.models import Post, User, Follow

# Register your models here.
admin.site.register(User)
admin.site.register(Post)
admin.site.register(Follow)
