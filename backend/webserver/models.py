from email.policy import default
from random import choices
from unittest.util import _MAX_LENGTH
from django.db import models


class Author(models.Model):
    display_name = models.CharField(max_length=200)
    profile_image = models.CharField(max_length=250)
    github_handle = models.CharField(max_length=200)

    def __str__(self):
        return self.display_name

class FollowRequest(models.Model):
    sender =  models.ForeignKey(Author,related_name='sender',on_delete=models.CASCADE)
    receiver =  models.ForeignKey(Author,related_name='receiver',on_delete=models.CASCADE) 


class Follow(models.Model):
    follower = models.ForeignKey(Author,related_name='follower',on_delete=models.CASCADE)
    followee = models.ForeignKey(Author,related_name='followee',on_delete=models.CASCADE)

class Post(models.Model):

    author = models.ForeignKey(Author,on_delete=models.CASCADE)

    created_at = models.CharField(max_length=200,null=False,blank=False)
    edited_at = models.CharField(max_length=200)

    title = models.CharField(max_length=200)

    description = models.CharField(max_length=200)

    source = models.CharField(max_length=200)

    origin = models.CharField(max_length=200)

    unlisted = models.BooleanField(default=False) 

    VISIBILITY_CHOICES = [
        ("PUBLIC","Public"),
        ("FRIENDS","Friends"),
    ]

    visibility = models.CharField(max_length=200,choices=VISIBILITY_CHOICES,default="PUBLIC")

    CONTENT_TYPE_CHOICES = [
        ("text/plain","Plain text"),
        ("text/markdown","Markdown text")
    ]

    content_type = models.CharField(max_length=200,choices=CONTENT_TYPE_CHOICES,default="text/plain")



# Create your models here.
