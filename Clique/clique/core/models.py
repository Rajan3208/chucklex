# models.py
from django.db import models
from django.contrib.auth import get_user_model
import uuid
from datetime import datetime
from django.utils import timezone

User = get_user_model()

# Create your models here.
class Profile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    id_user = models.IntegerField()
    bio = models.TextField(blank=True)
    profileimg = models.ImageField(upload_to='profile_images', default='blank-profile-picture.png')
    coverimg = models.ImageField(upload_to='cover_images', default='default-cover.jpg')
    location = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.user.username

class Post(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    user = models.CharField(max_length=100)
    image = models.ImageField(upload_to='post_images')
    caption = models.TextField()
    created_at = models.DateTimeField(default=datetime.now)
    no_of_likes = models.IntegerField(default=0)

    def __str__(self):
        return self.user
    
class LikePost(models.Model):
    post_id=models.CharField(max_length=500)
    username = models.CharField(max_length=100)
    
    def __str__(self):
        return f"{self.username} likes post {self.post_id}"

class FollowersCount(models.Model):
    follower = models.CharField(max_length=100) 
    user = models.CharField(max_length=100) 
    
    def __str__(self):
        return  self.user
    
class SavedPost(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'post')  
          
class Story(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.FileField(upload_to='stories')
    created_at = models.DateTimeField(default=timezone.now)
    expires_at = models.DateTimeField()

    def save(self, *args, **kwargs):
        if not self.expires_at:
            self.expires_at = self.created_at + timezone.timedelta(hours=24)
        super().save(*args, **kwargs)

    @property
    def is_expired(self):
        return timezone.now() > self.expires_at    