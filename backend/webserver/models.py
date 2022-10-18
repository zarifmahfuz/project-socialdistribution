from email.policy import default
from django.db import models


class Author(models.Model):
    display_name = models.CharField(max_length=200)
    profile_image = models.CharField(max_length=250)
    github_handle = models.CharField(max_length=200)

    def __str__(self):
        return self.display_name

class FollowRequest(models.Model):
    sender =  models.ForeignKey(Author, related_name='follow_requests_sent', on_delete=models.CASCADE)
    receiver =  models.ForeignKey(Author, related_name='follow_requests_received', on_delete=models.CASCADE) 

class Follow(models.Model):
    follower = models.ForeignKey(Author, related_name='following_authors', on_delete=models.CASCADE)
    followee = models.ForeignKey(Author, related_name='followed_by_authors', on_delete=models.CASCADE)

class Post(models.Model):

    author = models.ForeignKey(Author,on_delete=models.CASCADE)
    created_at = models.DateTimeField(verbose_name="date created",auto_now_add=True)
    edited_at = models.DateTimeField("date edited",null=True)
    title = models.CharField(max_length=300)
    description = models.TextField(blank=True)
    source = models.CharField(max_length=200,default='')
    origin = models.CharField(max_length=200,default='')
    unlisted = models.BooleanField(default=False) 

    VISIBILITY_CHOICES = [
        ("PUBLIC","Public"),
        ("FRIENDS","Friends"),
        ("PRIVATE","Private")
    ]
    visibility = models.CharField(max_length=200,choices=VISIBILITY_CHOICES,default="PUBLIC")
    CONTENT_TYPE_CHOICES = [
        ("text/plain","Plain text"),
        ("text/markdown","Markdown text")
    ]
    content_type = models.CharField(max_length=200,choices=CONTENT_TYPE_CHOICES,default="text/plain")
    content = models.TextField(blank=True)

class Comment(models.Model):
    author = models.ForeignKey(Author,on_delete=models.CASCADE)
    post = models.ForeignKey(Post,on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    CONTENT_TYPE_CHOICES = [
        ("text/plain","Plain text"),
        ("text/markdown","Markdown text")
    ]
    content_type = models.CharField(max_length=200,choices=CONTENT_TYPE_CHOICES,default="text/plain")


class Like(models.Model):
    author = models.ForeignKey(Author,on_delete=models.CASCADE)
    post = models.ForeignKey(Post,on_delete=models.CASCADE,null=True)
    comment = models.ForeignKey(Comment,on_delete=models.CASCADE,null=True)

class Inbox(models.Model):
    target_author = models.ForeignKey(Author,on_delete=models.CASCADE)
    follow_request_acceptor = models.ForeignKey(Author, related_name='accepted_follow_requests', on_delete=models.CASCADE, verbose_name='author who accepted the follow request', null=True)
    follow_request_sender = models.ForeignKey(Author, related_name='sent_follow_requests', on_delete=models.CASCADE, verbose_name='author who sent the follow request', null=True)
    post = models.ForeignKey(Post,on_delete=models.CASCADE,null=True)
    comment = models.ForeignKey(Comment,on_delete=models.CASCADE,null=True)
    like = models.ForeignKey(Like,on_delete=models.CASCADE,null=True)
