from django.db import models
from django.contrib.auth import get_user_model
from datetime import datetime
import uuid

# Je récupère le modèle User
User = get_user_model()


class Profile(models.Model):
    # Pour gérer objects dans mes view
    objects = models.Manager()

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    id_user = models.IntegerField()
    bio = models.TextField(blank=True)
    # Je veux une image de profil par défaut, elle sera stockée dans 'media'
    profile_img = models.ImageField(upload_to='profile_images', default='blank-profile-picture.png')
    location = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.user.username


class Post(models.Model):
    # Pour gérer objects dans mes view
    objects = models.Manager()

    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    # On indiquera le username de celui qui crée le Post
    user = models.CharField(max_length=100)
    image = models.ImageField(upload_to='post_images')
    caption = models.TextField()
    created_at = models.DateTimeField(default=datetime.now)
    no_of_likes = models.IntegerField(default=0)

    def __str__(self):
        return self.user


class LikePost(models.Model):
    # Pour gérer objects dans mes view
    objects = models.Manager()

    post_id = models.CharField(max_length=500)
    username = models.CharField(max_length=100)

    def __str__(self):
        return self.username


class FollowersCount(models.Model):
    # Pour gérer objects dans mes view
    objects = models.Manager()

    follower = models.CharField(max_length=100)
    user = models.CharField(max_length=100)

    def __str__(self):
        return self.user
