from django.db import IntegrityError, transaction
from django.shortcuts import get_object_or_404
from django.http import Http404
from django.contrib.auth import authenticate, login, logout
from rest_framework.views import APIView
from .models import Author, FollowRequest, Inbox, Post,Follow
from .serializers import AuthorSerializer, AuthorRegistrationSerializer, FollowRequestSerializer, CreatePostSerializer, PostSerializer, UpdatePostSerializer,  SendPrivatePostSerializer, SendFollowRequestSerializer
from rest_framework.response import Response
from rest_framework.authentication import BasicAuthentication
from rest_framework import status, permissions
from django.utils.timezone import utc
import datetime

class AuthorsView(APIView):
    authentication_classes = [BasicAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        authors = Author.objects.all()
        serializer = AuthorSerializer(authors, many=True, context={'request': request})

        return Response(serializer.data, status=status.HTTP_200_OK)
        

class AuthorDetailView(APIView):
    authentication_classes = [BasicAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_author(self,pk):
        author = get_object_or_404(Author,pk=pk)
        return author

    
    def get(self, request, pk, *args, **kwargs):
        author = self.get_author(pk)
        serializer = AuthorSerializer(author, context={'request': request})

        return Response(serializer.data, status=status.HTTP_200_OK)

    
    def post(self, request, pk, *args, **kwargs):
        author = self.get_author(pk)
        serializer = AuthorSerializer(instance=author, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class AuthorRegistrationView(APIView):
    def post(self, request):
        serializer = AuthorRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    def post(self, request):
        if 'username' not in request.data or 'password' not in request.data:
            return Response({'message': 'Credentials missing'}, status=status.HTTP_400_BAD_REQUEST)
        username = request.data['username']
        password = request.data['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return Response({'message': 'Login Success'}, status=status.HTTP_200_OK)
        return Response({'message': 'Invalid Credentials'}, status=status.HTTP_401_UNAUTHORIZED)


class LogoutView(APIView):
    def post(self, request):
        logout(request)
        return Response({'message': 'Successfully Logged out'}, status=status.HTTP_200_OK)

class PostView(APIView):
    authentication_classes = [BasicAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_author(self,pk):
        author = get_object_or_404(Author,pk=pk)
        return author
    def get_post(self,post_id,author_id):
        post = get_object_or_404(Post,id=post_id,author=author_id)
        return post
    
    def get(self,request,pk,post_id, *args, **kwargs):
        author =self.get_author(pk=pk)
        post = self.get_post(post_id,author.id)
        if post.visibility == "PUBLIC":
            serializer = PostSerializer(post, context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            raise Http404

    def post(self, request, pk,post_id, *args, **kwargs):
        author = self.get_author(pk=pk)
        post = self.get_post(post_id,author.id)

        if post.visibility == "PUBLIC":   
            if author.id == request.user.id:
                post = self.get_post(post_id,author.id)
                date_edited = datetime.datetime.utcnow().replace(tzinfo=utc)
                post.edited_at = date_edited
                serializer = UpdatePostSerializer(instance=post,data=request.data,partial=True,context={'request': request})
                if serializer.is_valid():
                    serializer.save()
                    return Response(serializer.data, status=status.HTTP_200_OK)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({'message': 'You cannot edit another authors post'}, status=status.HTTP_400_BAD_REQUEST) 
        else:
            return Response({'message': 'You can only edit public posts'}, status=status.HTTP_400_BAD_REQUEST)
        

    def delete(self,request,pk,post_id,*args,**kwargs):
        author =self.get_author(pk=pk)
        post = self.get_post(post_id,author.id)
        if post.visibility == "PUBLIC":
            if author.id == request.user.id:
                post = self.get_post(post_id,author.id)
                post.delete()
            else:
                return Response({'message': 'You cannot delete another authors post'}, status=status.HTTP_400_BAD_REQUEST) 
            return Response({"message":"Object deleted!"}, status=status.HTTP_200_OK)
        else:
            return Response({'message': 'You can only delete public posts'}, status=status.HTTP_400_BAD_REQUEST)
    
   
    
    



class AllPosts(APIView):
    authentication_classes = [BasicAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    def get_author(self,pk):
        author = get_object_or_404(Author,pk=pk)
        return author

    def get(self, request,pk, *args, **kwargs):
        author = self.get_author(pk)
        posts = Post.objects.filter(author=author.id).all()
        serializer = PostSerializer(posts, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    
    def post(self, request, pk, *args, **kwargs):
        author = self.get_author(pk)
        serializer = CreatePostSerializer(data=request.data)
        if author.id == request.user.id:
            if serializer.is_valid():
                new_post = Post.objects.create(
                    author=author,
                    title=serializer.data["title"],
                    description=serializer.data["description"],
                    unlisted=serializer.data["unlisted"],
                    content_type=serializer.data["content_type"],
                    content=serializer.data["content"],
                    visibility=serializer.data["visibility"]
                )
                if new_post.visibility == "FRIENDS" or new_post.visibility == "PUBLIC":
                    author_one_followers = author.followed_by_authors
                    for follow in author_one_followers.iterator():
                        with transaction.atomic():
                            Inbox.objects.create(target_author=follow.follower,post=new_post)
                elif new_post.visibility == "PRIVATE":
                    private_post_serializer = SendPrivatePostSerializer(data=request.data)
                    if private_post_serializer.is_valid():
                        
                        try:
                            receiver =  Author.objects.get(pk=private_post_serializer.data['receiver']['id'])    
                        except Author.DoesNotExist:
                            return Response({'message': f'receiver author with id {private_post_serializer.data["receiver"]["id"]} does not exist'}, status=status.HTTP_404_NOT_FOUND)
                        with transaction.atomic():
                            Inbox.objects.create(target_author=receiver, post=new_post)
                    else:
                        print("What are the errors",private_post_serializer.errors)        
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST) 

class FollowRequestsView(APIView):
    authentication_classes = [BasicAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, author_id):
        # TODO: for project part 2; will also need to look at the inbox of this author to fetch follow requests
        # received from remote authors
        author = get_object_or_404(Author, pk=author_id)
        serializer = FollowRequestSerializer(author.follow_requests_received.all(), many=True, context={'request': request})

        return Response(serializer.data, status=status.HTTP_200_OK)


class FollowRequestProcessor(object):
    def __init__(self, request, author_id):
        self.request = request
        self.author_id = author_id
        self.response = self.send_request(request, author_id)
    
    def send_request(self, request, author_id):
        serializer = SendFollowRequestSerializer(data=request.data)
        if serializer.is_valid():
            if (serializer.data["sender"]["url"] == serializer.data["receiver"]["url"]):
                return Response(
                    {'message': 'author cannot send follow request to themself'}, status=status.HTTP_400_BAD_REQUEST
                )
            
            # TODO: for project part 2; use the 'url's to determine if a given author is a remote one or a local one
            # if the <host> section of a url is not our host, it's a remote author
            # assume that both the sender and the receiver are local authors for now
            try:
                # TODO: for project part 2; if the receiver is a remote author, we need to send a POST request
                # to the inbox of the remote author; of course we also won't create a local follow request object
                receiver = Author.objects.get(pk=author_id)
            except Author.DoesNotExist:
                return Response({'message': f'author_id {author_id} does not exist'}, status=status.HTTP_404_NOT_FOUND)
            try:
                # TODO: for project part 2; if the sender is a remote author, we might need to add another field
                # to the inbox entity 'remote_follow_request_sender_url' to store a local representation of that follow
                # request or find some other solution that works
                sender = Author.objects.get(pk=serializer.data['sender']['id'])
            except Author.DoesNotExist:
                return Response({'message': f'sender author with id {serializer.data["sender"]["id"]} does not exist'}, 
                                status=status.HTTP_404_NOT_FOUND)
            try:
                # https://docs.djangoproject.com/en/4.1/topics/db/transactions/#controlling-transactions-explicitly
                with transaction.atomic():
                    follow_request = FollowRequest.objects.create(sender=sender, receiver=receiver)
                    # update the inbox of the receiver
                    Inbox.objects.create(target_author=receiver, follow_request_sender=sender)

                # TODO: return the new inbox item when we have an Inbox serializer
                return Response({'message': 'OK'}, status=status.HTTP_201_CREATED)
            except IntegrityError:
                return Response({'message': 'this follow request already exists'}, status=status.HTTP_409_CONFLICT)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def get_response(self):
        return self.response


class InboxView(APIView):
    authentication_classes = [BasicAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, author_id):
        if 'type' not in request.data:
            return Response({'message': 'must specify the type of inbox'}, status=status.HTTP_400_BAD_REQUEST)
        if request.data['type'] == 'follow':
            return FollowRequestProcessor(request, author_id).get_response()
        else:
            return Response({'message': "unknown 'type'"}, status=status.HTTP_400_BAD_REQUEST)
