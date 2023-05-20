from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

# user model for post
class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.CharField(max_length=500, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    like = models.ManyToManyField(User, blank=True, related_name="liked_user")

    def __str__(self):
        return self.user.username

# user model for following
class Follow(models.Model):
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name="following") # user following
    following = models.ForeignKey(User, on_delete=models.CASCADE, related_name="follower") # user with follower
