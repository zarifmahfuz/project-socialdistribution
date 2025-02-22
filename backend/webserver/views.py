from django.db import IntegrityError, transaction
from django.shortcuts import get_object_or_404
from django.contrib.auth import authenticate, login, logout
from urllib.parse import urljoin
from rest_framework.views import APIView
from .models import Author, Follow, FollowRequest, Inbox, Post, Node, RemoteAuthor, RemotePost, Like, Comment
from .serializers import (AcceptOrDeclineFollowRequestSerializer, 
                          AuthorSerializer, 
                          AuthorRegistrationSerializer, 
                          FollowRequestSerializer, 
                          FollowerSerializer, 
                          SendFollowRequestSerializer, 
                          CreatePostSerializer, 
                          PostSerializer, 
                          UpdatePostSerializer,  
                          SendPrivatePostSerializer,
                          InboxSerializer,
                          RemoveFollowerSerializer,
                          AddNodeSerializer,
                          NodesListSerializer,
                          SendPostInboxSerializer,
                          SendLikeSerializer,
                          LikeSerializer,
                          CreateImagePostSerializer,
                          SendCommentInboxSerializer,
                          CommentSerializer,)
from rest_framework.response import Response
from rest_framework.authentication import BasicAuthentication
from rest_framework import status, permissions
from django.utils.timezone import utc
import datetime
from .utils import (BasicPagination, 
                    PaginationHandlerMixin, 
                    IsRemoteGetOnly, 
                    IsRemotePostOnly, 
                    is_remote_request, 
                    join_urls,
                    format_uuid_without_dashes,
                    get_comment_id_from_url)
from .api_client import http_request
import logging
import concurrent.futures
from .custom_renderers import PNGRenderer, JPEGRenderer
import base64


logger = logging.getLogger(__name__)
external_request_timeout = 5

class AuthorsView(APIView, PaginationHandlerMixin):
    authentication_classes = [BasicAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = BasicPagination
    
    def get_serializer(self, request, queryset):
        return AuthorSerializer(queryset, many=True, context={'request': request})

    def get(self, request):
        authors = Author.objects.exclude(is_remote_user=True).exclude(is_admin=True).order_by("created_at")
        page = self.paginate_queryset(authors)
        if page is not None:
            serializer = self.get_paginated_response(
                self.get_serializer(request, page).data
            )
        else:
            serializer = self.get_serializer(request, authors)

        response_data = serializer.data
        if not is_remote_request(request):
            # TODO: implement synchronicity between local and remote pagination
            external_authors = []
            for node in Node.objects.all():
                try:
                    response, _ = http_request(method="GET", url=node.get_authors_url(), node=node,
                                               timeout=external_request_timeout)
                    if response == None:
                        continue
                except Exception as e:
                    logger.error("api_client.http_request came across an unexpected error: {}".format(e))
                    continue
                external_authors.extend(node.get_converter().convert_authors(response))
            
            # serializer.data does not seem to be mutable, so we have to do this (for now...)
            if "results" in serializer.data:
                response_data["results"].extend(external_authors)
            else:
                response_data.extend(external_authors)

        return Response(data=response_data, status=status.HTTP_200_OK)


class AuthorDetailView(APIView):
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsRemoteGetOnly]

    def get(self, request, pk):
        try:
            author = Author.objects.get(pk=pk)
        except Author.DoesNotExist:
            if not is_remote_request(request):
                # this is a local request and the requested author could exist on other nodes
                for node in Node.objects.all():
                    url = join_urls(node.get_authors_url(), pk)
                    if node.team == 11:
                        url = join_urls(node.get_authors_url(), format_uuid_without_dashes(pk))
                    res, _ = http_request("GET", url=url, node=node, expected_status=200,
                                        timeout=external_request_timeout)
                    if res is not None:
                        return Response(node.get_converter().convert_author(res), status=status.HTTP_200_OK)
            return Response({'message': 'Author not found'}, status=status.HTTP_404_NOT_FOUND)
            
        serializer = AuthorSerializer(author, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, pk, *args, **kwargs):
        author = get_object_or_404(Author,pk=pk)
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
    permission_classes = [IsRemoteGetOnly]

    def get_author(self,pk):
        author = get_object_or_404(Author,pk=pk)
        return author
    def get_post(self,post_id,author_id):
        post = get_object_or_404(Post,id=post_id,author=author_id)
        return post
    
    def get(self, request, pk, post_id):
        try:
            author = Author.objects.get(pk=pk)
        except Author.DoesNotExist:
            if is_remote_request(request):
                return Response({'message': 'Author not found'}, status=status.HTTP_404_NOT_FOUND)
            # this could be a remote author and the author_id could be stored in the remote_authors table already
            author = RemoteAuthor.objects.attempt_find(author_id=pk)
            if not author:
                return Response({'message': 'Author not found'}, status=status.HTTP_404_NOT_FOUND)
            post_url = join_urls(author.get_absolute_url(), "posts", post_id)
            res, _ = http_request("GET", url=post_url, node=author.node, expected_status=200)
            if res is None:
                return Response({'message': 'Post not found'}, status=status.HTTP_404_NOT_FOUND)
            return Response(author.node.get_converter().convert_post(res), status=status.HTTP_200_OK)

        post = self.get_post(post_id,author.id)
        if post.visibility == "PUBLIC":
            serializer = PostSerializer(post, context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            if post.author.id == request.user.id or Follow.objects.filter(follower=request.user.id,followee=post.author.id).count() > 0:
                serializer = PostSerializer(post, context={'request': request})
                return Response(serializer.data, status=status.HTTP_200_OK)

        return Response({'message': 'you are not authorized to view this post'}, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request, pk,post_id, *args, **kwargs):
        author = self.get_author(pk)
        post = self.get_post(post_id,author.id)

        if post.visibility == "PUBLIC":   
            if author.id == request.user.id:
                serializer = UpdatePostSerializer(instance=post,data=request.data,partial=True,context={'request': request})
                for field in request.data:
                    if field not in serializer.fields:
                        return Response({'message': 'You cannot edit this field'}, status=status.HTTP_400_BAD_REQUEST)
                if serializer.is_valid():
                    serializer.save(edited_at=datetime.datetime.utcnow().replace(tzinfo=utc))
                    data_dict = {"id":post.id}
                    data_dict.update(serializer.data)
                    return Response(data_dict, status=status.HTTP_200_OK)
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
                post.delete()
                return Response({"message":"Object deleted!"}, status=status.HTTP_200_OK)
            else:
                return Response({'message': 'You cannot delete another authors post'}, status=status.HTTP_400_BAD_REQUEST) 
        return Response({'message': 'You can only delete public posts'}, status=status.HTTP_400_BAD_REQUEST)


class ImagePostView(APIView):
    authentication_classes = [BasicAuthentication]
    # permission_classes = [IsRemoteGetOnly]
    renderer_classes = [PNGRenderer, JPEGRenderer]
    
    def get(self, request, author_id, post_id):
        try:
            post = Post.objects.get(id=post_id, author_id=author_id)
            if 'image' not in post.content_type:
                return Response({'message': 'Post is not an image post'}, status=status.HTTP_404_NOT_FOUND)

            # Known issue: Remote followers cannot view friends-only image posts because this is an architectural limitation
            # that is caused by a BS project specification (polling based system vs webhooks)
            unauthorized = post.visibility != 'PUBLIC' and post.author.id != request.user.id\
                and Follow.objects.filter(follower=request.user.id, followee=post.author.id).count() == 0
            if unauthorized:
                return Response({'message': 'You are not authorized to view this post'}, status=status.HTTP_400_BAD_REQUEST)

            response_content_type = post.content_type.split(';')[0]
            image = base64.b64decode(post.content.strip("b'").strip("'"))
            return Response(image, content_type=response_content_type, status=status.HTTP_200_OK)
        except Post.DoesNotExist:
            # TODO: might exist remotely
            return Response({'message': 'Image post not found'}, status=status.HTTP_404_NOT_FOUND)


class AllPosts(APIView, PaginationHandlerMixin):
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsRemoteGetOnly]
    pagination_class = BasicPagination

    def get_author(self,pk):
        author = get_object_or_404(Author,pk=pk)
        return author
    
    def get_serializer(self, request, queryset):
        return PostSerializer(queryset, many=True, context={'request': request})

    def get(self, request, pk):
        try:
            author = Author.objects.get(pk=pk)
        except Author.DoesNotExist:
            if is_remote_request(request):
                return Response({'message': 'Author not found'}, status=status.HTTP_404_NOT_FOUND)
            # the author could exist on a remote node
            author = RemoteAuthor.objects.attempt_find(author_id=pk)
            if not author:
                return Response({'message': 'Author not found'}, status=status.HTTP_404_NOT_FOUND)
            posts_url = join_urls(author.get_absolute_url(), "posts", self.get_pagination_string())
            res, _ = http_request("GET", url=posts_url, node=author.node, expected_status=200)
            if res is None:
                return Response({'message': 'Posts not found on remote node'}, status=status.HTTP_404_NOT_FOUND)
            return Response(author.node.get_converter().convert_posts(res), status=status.HTTP_200_OK)

        posts = author.post_set.exclude(unlisted=True).all().order_by("-created_at")
        page = self.paginate_queryset(posts)
        if page is not None:
            serializer = self.get_paginated_response(
                self.get_serializer(request, page).data
            )
        else:
            serializer = self.get_serializer(request, posts)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    
    def post(self, request, pk):
        author = get_object_or_404(Author, pk=pk)

        if 'content_type' not in request.data:
            return Response({'message': 'must specify content_type'}, status=status.HTTP_400_BAD_REQUEST)
        if 'base64' in request.data['content_type']:
            serializer = CreateImagePostSerializer(data=request.data)
        else:
            serializer = CreatePostSerializer(data=request.data)
    
        if author.id == request.user.id:
            if serializer.is_valid():
                new_post = serializer.save(author=author)
                
                if new_post.visibility == "FRIENDS":
                    new_post.send_to_followers(request)
                elif new_post.visibility == "PUBLIC":
                    new_post.send_to_all_authors(request)
                elif new_post.visibility == "PRIVATE":
                    private_post_serializer = SendPrivatePostSerializer(data=request.data)
                    if private_post_serializer.is_valid():
                        # TODO: handle the case where receiver is a remote author
                        try:
                            receiver =  Author.objects.get(pk=private_post_serializer.data['receiver']['id'])
                            Inbox.objects.create(target_author=receiver, post=new_post)  
                        except Author.DoesNotExist:
                            try:
                                node = Node.objects.get_node_with_url(
                                    private_post_serializer.data["receiver"]["url"]
                                )
                                url = join_urls(node.get_authors_url(), private_post_serializer.data["receiver"]["id"], 
                                                "inbox", ends_with_slash=True)
                                new_post.update_author_inbox_over_http(url, node, request.data["receiver"])
                            except Node.DoesNotExist:
                                return Response({
                                    'message': f'receiver author with id {private_post_serializer.data["receiver"]["id"]} does not exist'
                                    }, status=status.HTTP_404_NOT_FOUND)
                    else:
                        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

                response_dict = {"id": new_post.id}

                if "image" in new_post.content_type:
                    response_dict["url"] = new_post.get_image_url(request)
                else:
                    response_dict.update(serializer.data)

                return Response(response_dict, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST) 
        else:
            return Response({'message': 'You cannot create a post for another user'}, status=status.HTTP_400_BAD_REQUEST)


class AllPublicPostsView(APIView, PaginationHandlerMixin):
    pagination_class = BasicPagination

    def get_serializer(self, request, queryset):
        return PostSerializer(queryset, many=True, context={'request': request})
    
    def get_external_posts(self):
        external_posts = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            future_to_url = {}
            for node in Node.objects.all():
                node_converter = node.get_converter()
                url = node_converter.public_posts_url(node.api_url)
                if url is None:
                    continue
                future_to_url[executor.submit(
                    http_request, "GET", url=url, node=node, expected_status=200,
                )] = (url, node_converter)
            for future in concurrent.futures.as_completed(future_to_url):
                url, node_converter = future_to_url[future]
                try:
                    res, _ = future.result()
                    if res is None:
                        continue
                    external_posts.extend(node_converter.convert_posts(res, from_public_posts_url=True))
                except Exception as exc:
                    logger.error(f"{url} generated an exception: {exc}")
        return external_posts

    def get(self, request):
        """Returns recent public posts"""
        posts = Post.objects.exclude(unlisted=True).filter(visibility="PUBLIC").order_by("-created_at")
        page = self.paginate_queryset(posts)
        if page is not None:
            serializer = self.get_paginated_response(
                self.get_serializer(request, page).data
            )
        else:
            serializer = self.get_serializer(request, posts)

        response_data = serializer.data
        if not is_remote_request(request):
            external_posts = self.get_external_posts()
            if "results" in serializer.data:
                response_data["results"].extend(external_posts)
            else:
                response_data.extend(external_posts)

        return Response(response_data, status=status.HTTP_200_OK)


class AuthorLikedView(APIView):
    authentication_classes = [BasicAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, pk):
        try:
            author = Author.objects.get(pk=pk)
            author_likes = Like.objects.filter(author=author)
            queryset = author_likes.filter(post__isnull=False).filter(post__visibility="PUBLIC")\
                .union(author_likes.filter(comment__isnull=False).filter(comment__post__visibility="PUBLIC")).order_by("created_at")
            serializer = LikeSerializer(queryset, many=True, context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Author.DoesNotExist:
            if is_remote_request(request):
                return Response({'message': 'Author not found'}, status=status.HTTP_404_NOT_FOUND)
            # pk could represent a remote author
            remote_author = RemoteAuthor.objects.attempt_find(pk)
            if remote_author is None:
                return Response({'message': 'Remote author not found'}, status=status.HTTP_404_NOT_FOUND)
            node = remote_author.node
            node_converter = node.get_converter()
            url = node_converter.url_to_get_author_liked_objects(remote_author.get_absolute_url())
            res, status_code = http_request("GET", url, node=node)
            if res is None:
                return Response({'message': 'Failed to get likes made by a remote author'}, status=status_code)
            return Response(node_converter.convert_likes(res), status=status.HTTP_200_OK)

class PostLikesView(APIView):
    authentication_classes = [BasicAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, pk, post_id):
        try:
            author = Author.objects.get(pk=pk)
            post = get_object_or_404(Post, pk=post_id, author=author)
            serializer = LikeSerializer(post.like_set.all(), many=True, context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Author.DoesNotExist:
            if is_remote_request(request):
                return Response({'message': 'Author not found'}, status=status.HTTP_404_NOT_FOUND)
            # local author fetching likes from a remote post
            remote_author = RemoteAuthor.objects.attempt_find(pk)
            if remote_author is None:
                return Response({'message': 'Remote author not found'}, status=status.HTTP_404_NOT_FOUND)
            node = remote_author.node
            node_converter = node.get_converter()
            url = node_converter.url_to_get_likes_at(remote_author.get_absolute_url(), post_id)
            res, status_code = http_request("GET", url, node=node)
            if res is None:
                return Response({'message': 'Failed to get likes on a remote post'}, status=status_code)
            return Response(node_converter.convert_likes(res), status=status.HTTP_200_OK)


class CommentLikesView(APIView):
    authentication_classes = [BasicAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, author_id, post_id, comment_id):
        try:
            author = Author.objects.get(pk=author_id)
            post = get_object_or_404(Post, pk=post_id, author=author)
            comment = get_object_or_404(Comment, pk=comment_id, post=post)
            serializer = LikeSerializer(comment.like_set.all(), many=True, context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Author.DoesNotExist:
            if is_remote_request(request):
                return Response({'message': 'Author not found'}, status=status.HTTP_404_NOT_FOUND)
            # local author fetching likes from a remote comment
            remote_author = RemoteAuthor.objects.attempt_find(author_id)
            if remote_author is None:
                return Response({'message': 'Remote author not found'}, status=status.HTTP_404_NOT_FOUND)
            node = remote_author.node
            node_converter = node.get_converter()
            url = node_converter.url_to_get_likes_at(remote_author.get_absolute_url(), post_id, comment_id)
            res, status_code = http_request("GET", url, node=node)
            if res is None:
                return Response({'message': 'Failed to get likes on a remote comment'}, status=status_code)
            return Response(node_converter.convert_likes(res), status=status.HTTP_200_OK)


class FollowRequestsView(APIView):
    authentication_classes = [BasicAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, author_id):
        # TODO: for project part 2; will also need to look at the inbox of this author to fetch follow requests
        # received from remote authors
        author = get_object_or_404(Author, pk=author_id)
        serializer = FollowRequestSerializer(author.follow_requests_received.all(), many=True, context={'request': request})

        return Response(serializer.data, status=status.HTTP_200_OK)


class FollowRequestDetailView(APIView):
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsRemoteGetOnly]
    
    def delete(self, request, author_id, foreign_author_id):
        """Decline a follow request"""
        serializer = AcceptOrDeclineFollowRequestSerializer(data=request.data)
        if serializer.is_valid():
            queryset = FollowRequest.objects.filter(sender=foreign_author_id, receiver=author_id)\
                .union(FollowRequest.objects.filter(remote_sender=foreign_author_id, receiver=author_id))
            if len(queryset) > 0:
                follow_request = queryset[0]
                follow_request.delete()
                return Response({'message': 'Follow request declined'}, status=status.HTTP_200_OK)
            else:
                return Response({'message': 'Follow request not found'}, status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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

            try:
                receiver = Author.objects.get(pk=author_id)
            except Author.DoesNotExist:
                # receiver could be a remote author
                try:
                    node = Node.objects.get_node_with_url(serializer.data["receiver"]["url"])
                    node_converter = node.get_converter()

                    if not node_converter.skip_follow_check_before_sending_follow_request():
                        # check if the sender already follows the receiver
                        url = join_urls(serializer.data["receiver"]["url"], "followers", serializer.data["sender"]["id"])

                        res, _ = http_request("GET", url, expected_status=node_converter.expected_status_code("check_for_follower"), 
                                            node=node)
                        if res is not None:
                            return Response(
                                {'message': 'sender already follows receiver'}, status=status.HTTP_400_BAD_REQUEST
                            )

                    # send a post request to the receiver's inbox
                    url = node_converter.url_to_send_follow_request_at(serializer.data["receiver"]["url"])
                    res, res_status = http_request("POST", url, node=node,
                                                   expected_status=node_converter.expected_status_code("send_follow_request"), 
                                                   json=node_converter.send_follow_request(request.data, request),
                                                   timeout=node.post_request_timeout())
                    if res is None:
                        return Response("Failed to send remote follow request due to remote node failure", status=res_status)
                    return Response({'message': 'OK'}, status=status.HTTP_201_CREATED)

                except Node.DoesNotExist:
                    return Response({'message': f'receiver with id {author_id} does not exist'}, status=status.HTTP_404_NOT_FOUND)

            try:
                sender = Author.objects.get(pk=serializer.data['sender']['id'])
            except Author.DoesNotExist:
                # sender could be remote author
                try:
                    node = Node.objects.get_node_with_url(serializer.data["sender"]["url"])
                    node_converter = node.get_converter()
                    # get_or_create returns (object, created)
                    sender = RemoteAuthor.objects.get_or_create(
                        id=node_converter.remote_follow_request_sender_id(serializer.data), node=node)[0]

                except Node.DoesNotExist:
                    return Response({'message': f'sender author with id {serializer.data["sender"]["id"]} does not exist'}, 
                                    status=status.HTTP_404_NOT_FOUND)
            
            if isinstance(sender, Author):
                follow = Follow.objects.filter(follower=sender, followee=receiver)
            else:
                follow = Follow.objects.filter(remote_follower=sender, followee=receiver)
            if follow.count() > 0:
                return Response({'message': 'sender already follows the receiver'}, status=status.HTTP_400_BAD_REQUEST)

            try:
                # https://docs.djangoproject.com/en/4.1/topics/db/transactions/#controlling-transactions-explicitly
                with transaction.atomic():
                    if isinstance(sender, Author):
                        follow_request = FollowRequest.objects.create(sender=sender, receiver=receiver)
                    else:
                        follow_request = FollowRequest.objects.create(remote_sender=sender, receiver=receiver)
                    # update the inbox of the receiver
                    Inbox.objects.create(target_author=receiver, follow_request_received=follow_request)

                # TODO: return the new inbox item when we have an Inbox serializer
                return Response({'message': 'OK'}, status=status.HTTP_201_CREATED)
            except IntegrityError:
                return Response({'message': 'this follow request already exists'}, status=status.HTTP_409_CONFLICT)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get_response(self):
        return self.response


class RemotePostProcessor(object):
    def __init__(self, request, author_id):
        self.request = request
        self.author_id = author_id
        self.response = self.update_inbox_with_post(request, author_id)
    
    def update_inbox_with_post(self, request, author_id):
        target_author = get_object_or_404(Author, pk=author_id)
        if "post" not in request.data:
            return Response({'message': "'post' field is missing in the request payload"},
                            status=status.HTTP_400_BAD_REQUEST)
        serializer = SendPostInboxSerializer(data=request.data["post"])
        if serializer.is_valid():
            try:
                node = Node.objects.get_node_with_url(serializer.data["author"]["url"])
                remote_author = RemoteAuthor.objects.get_or_create(
                    id=serializer.data["author"]["id"], node=node)[0]
                remote_post = RemotePost.objects.get_or_create(
                    id=serializer.data["id"], author=remote_author)[0]
                
                # using get_or_create here because other groups might abuse this api endpoint and
                # try to create redundant inbox items
                Inbox.objects.get_or_create(target_author=target_author, remote_post=remote_post)
                return Response({'message': 'inbox updated'}, status=status.HTTP_201_CREATED)
            except Node.DoesNotExist:
                return Response({'message': 'unidentifiable node'}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def get_response(self):
        return self.response


class LikePostProcessor(object):
    def __init__(self, request, author_id):
        self.request = request
        self.author_id = author_id
        self.response = self.send_like(request, author_id)

    def duplicate_like_attempt(self, actor, entity):
        if isinstance(actor, Author) and isinstance(entity, Post):
            return Like.objects.filter(author=actor, post=entity).count() > 0
        elif isinstance(actor, Author) and isinstance(entity, Comment):
            return Like.objects.filter(author=actor, comment=entity).count() > 0
        elif isinstance(actor, RemoteAuthor) and isinstance(entity, Post):
            return Like.objects.filter(remote_author=actor, post=entity).count() > 0
        else:
            return Like.objects.filter(remote_author=actor, comment=entity).count() > 0

    def create_like(self, actor, entity):
        if isinstance(actor, Author) and isinstance(entity, Post):
            return Like.objects.create(author=actor, post=entity)
        elif isinstance(actor, Author) and isinstance(entity, Comment):
            return Like.objects.create(author=actor, comment=entity)
        elif isinstance(actor, RemoteAuthor) and isinstance(entity, Post):
            return Like.objects.create(remote_author=actor, post=entity)
        else:
            return Like.objects.create(remote_author=actor, comment=entity)

    def send_like(self, request, author_id):
        # three cases -
        # local author can be sending a like to another local author
        # local author could be sending a like to a remote author
        # remote author could be sending a like to a local author
        if "post" not in request.data and "comment_url" not in request.data:
            return Response({'message': 'You need to specify either a post or a comment to like'}, status=status.HTTP_400_BAD_REQUEST)
        serializer = SendLikeSerializer(data=request.data)
        if serializer.is_valid():
            try:
                author = Author.objects.get(pk=author_id)
                if "post" in serializer.data:
                    entity_to_like = get_object_or_404(Post, pk=serializer.data["post"]["id"], author=author)
                else:
                    comment_id = get_comment_id_from_url(serializer.data["comment_url"])
                    entity_to_like = get_object_or_404(Comment, pk=comment_id, author=author)
                try:
                    # local author sending a like to a local author
                    actor = Author.objects.get(pk=serializer.data["author"]["id"])
                    if self.duplicate_like_attempt(actor, entity_to_like):
                        return Response({'message': 'Cannot like an object more than once'}, status=status.HTTP_400_BAD_REQUEST)
                    like = self.create_like(actor, entity_to_like)
                except Author.DoesNotExist:
                    # remote author sending a like to a local author
                    try:
                        node = Node.objects.get_node_with_url(serializer.data["author"]["url"])
                        actor = RemoteAuthor.objects.get_or_create(id=serializer.data['author']['id'],
                                                                   node=node)[0]
                        if self.duplicate_like_attempt(actor, entity_to_like):
                            return Response({'message': 'Cannot like an object more than once'}, status=status.HTTP_400_BAD_REQUEST)
                        like = self.create_like(actor, entity_to_like)
                    except Node.DoesNotExist:
                        return Response({'message': 'unidentifiable node'}, status=status.HTTP_400_BAD_REQUEST)

                Inbox.objects.create(target_author=author, like=like)
                return Response({'message': 'OK'}, status=status.HTTP_201_CREATED)
            except Author.DoesNotExist:
                if is_remote_request(request):
                    return Response({'message': 'Author not found'}, status=status.HTTP_404_NOT_FOUND)
                # local author could be sending a like to a remote author
                remote_author = RemoteAuthor.objects.attempt_find(author_id)
                if remote_author is None:
                    return Response({'message': 'Author not found'}, status=status.HTTP_404_NOT_FOUND)
                node = remote_author.node
                node_converter = node.get_converter()
                post_id = serializer.data["post"]["id"] if "post" in serializer.data else None
                url = node_converter.url_to_send_like_at(remote_author.get_absolute_url(), post_id)
                if url is None:
                    return Response({'message': 'Remote entity does not support likes'}, status=status.HTTP_400_BAD_REQUEST)
                res, status_code = http_request("POST", url, node=node, 
                                                json=node_converter.send_like_inbox(request), timeout=node.post_request_timeout())
                if res is None:
                    return Response({'message': 'Failed to like a remote entity'}, status=status_code)
                return Response({'message': 'OK'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get_response(self):
        return self.response


class CommentOnPostProcessor(object):
    def __init__(self, request, author_id):
        self.request = request
        self.author_id = author_id
        self.response = self.send_comment(request, author_id)
    
    def send_comment(self, request, author_id):
        serializer = SendCommentInboxSerializer(data=request.data)
        if serializer.is_valid():
            try:
                author = Author.objects.get(pk=author_id)
                post = get_object_or_404(Post, pk=serializer.data['post']['id'], author=author)

                try:
                    actor = Author.objects.get(id=serializer.data['author']['id'])
                    comment = Comment.objects.create(
                        author=actor, post=post, comment=serializer.data['comment'], content_type=serializer.data['content_type'])
                    
                except Author.DoesNotExist:
                    # remote author could be sending a comment to a local author
                    try:
                        node = Node.objects.get_node_with_url(serializer.data["author"]["url"])
                        actor = RemoteAuthor.objects.get_or_create(id=serializer.data['author']['id'],
                                                                   node=node)[0]
                        comment = Comment.objects.create(
                            remote_author=actor, post=post, comment=serializer.data['comment'], content_type=serializer.data['content_type'])
                    except Node.DoesNotExist:
                        return Response({'message': 'unidentifiable node'}, status=status.HTTP_400_BAD_REQUEST)
                # send the comment to the post author's inbox
                Inbox.objects.create(target_author=author, comment=comment)
                return Response({'message': 'OK'}, status=status.HTTP_201_CREATED)
            except Author.DoesNotExist:
                if is_remote_request(request):
                    return Response({'message': 'Author not found'}, status=status.HTTP_404_NOT_FOUND)
                # Our frontend could be sending a comment on a post from a remote author
                # Can we find a remote author with the given author_id?
                remote_author = RemoteAuthor.objects.attempt_find(author_id)
                if remote_author is None:
                    return Response({'message': 'Author not found'}, status=status.HTTP_404_NOT_FOUND)
                node = remote_author.node
                node_converter = node.get_converter()
                url = node_converter.url_to_send_comment_at(remote_author.get_absolute_url(), serializer.data['post']['id'])
                if url is None:
                    return Response({'message': 'Remote entity does not support comments'}, status=status.HTTP_400_BAD_REQUEST)
                # send the comment to the remote author's inbox
                res, status_code = http_request("POST", url, node=node, 
                                                json=node_converter.send_comment_inbox(request),
                                                timeout=node.post_request_timeout())
                if res is None:
                    return Response({'message': 'Failed to send comment to remote post'}, status=status_code)
                return Response({'message': 'OK'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def get_response(self):
        return self.response


class CommentsView(APIView):
    authentication_classes = [BasicAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, author_id, post_id):
        try:
            author = Author.objects.get(pk=author_id)
            post = get_object_or_404(Post, pk=post_id, author=author)
            if post.visibility != "PUBLIC" and request.user.id != author.id:
                return Response({'message': 'You are not authorized to view comments of this post'}, status=status.HTTP_403_FORBIDDEN)
            serializer = CommentSerializer(post.comment_set.order_by("-created_at").all(), many=True, context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Author.DoesNotExist:
            if is_remote_request(request):
                return Response({'message': 'Author not found'}, status=status.HTTP_404_NOT_FOUND)
            # Frontend could be trying to fetch comments of a remote post
            remote_author = RemoteAuthor.objects.attempt_find(author_id)
            if remote_author is None:
                return Response({'message': 'Author not found'}, status=status.HTTP_404_NOT_FOUND)
            node = remote_author.node
            node_converter = node.get_converter()
            url = node_converter.url_to_get_comments_at(remote_author.get_absolute_url(), post_id)
            res, status_code = http_request("GET", url, node=node)
            if res is None:
                return Response({'message': 'Failed to get comments from remote post'}, status=status_code)
            return Response(node_converter.convert_comments(res), status=status.HTTP_200_OK)


class FollowersView(APIView):
    authentication_classes = [BasicAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, author_id):
        author = get_object_or_404(Author, pk=author_id)
        serializer = FollowerSerializer(author.followed_by_authors.all(), many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)


class FollowersDetailView(APIView):
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsRemoteGetOnly]
    
    def get(self, request, author_id, foreign_author_id):
        queryset = Follow.objects\
            .filter(follower=foreign_author_id, followee=author_id)\
            .union(Follow.objects.filter(remote_follower=foreign_author_id, followee=author_id))
        if len(queryset) > 0:
            return Response({'message': 'follower indeed'}, status=status.HTTP_200_OK)
        # BUG TODO: author_id could be a remote author! In that case, we need to forward this request to all the
        # nodes we are connected to.
        return Response({'message': f'{foreign_author_id} is not a follower of {author_id}'}, 
                        status=status.HTTP_404_NOT_FOUND)

    def put(self, request, author_id, foreign_author_id):
        if author_id == foreign_author_id:
            return Response({'message': 'author cannot add themself as a follower'}, status=status.HTTP_400_BAD_REQUEST)
        serializer = AcceptOrDeclineFollowRequestSerializer(data=request.data)
        if serializer.is_valid():
            # it is safe to assume that the followee will be someone from our server
            # because they are accepting the follow request
            followee = get_object_or_404(Author, pk=author_id)
            
            # foreign_author_id could be a local or a remote author
            try:
                follower = Author.objects.get(pk=foreign_author_id)
            except Author.DoesNotExist:
                follower = get_object_or_404(RemoteAuthor, pk=foreign_author_id)
            try:
                if isinstance(follower, Author):
                    follow_request = FollowRequest.objects.get(sender=follower, receiver=followee)
                else:
                    follow_request = FollowRequest.objects.get(remote_sender=follower, receiver=followee)
            except FollowRequest.DoesNotExist:
                error_message = 'matching follow request does not exist; you need to create a follow request before '\
                    'you can accept one'
                return Response({'message': error_message}, status=status.HTTP_400_BAD_REQUEST)
            
            try:
                with transaction.atomic():
                    if isinstance(follower, Author):
                        Follow.objects.create(follower=follower, followee=followee)
                    else:
                        Follow.objects.create(remote_follower=follower, followee=followee)
                    follow_request.delete()

                return Response({'message': 'OK'}, status=status.HTTP_201_CREATED)
            except IntegrityError:
                return Response({'message': 'follower already exists'}, status=status.HTTP_409_CONFLICT)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, author_id, foreign_author_id):
        serializer = RemoveFollowerSerializer(data=request.data)
        if serializer.is_valid():
            queryset = Follow.objects\
                .filter(follower=foreign_author_id, followee=author_id)\
                .union(Follow.objects.filter(remote_follower=foreign_author_id, followee=author_id))
            if len(queryset) > 0:
                follow = queryset[0]
                follow.delete()
                return Response({'message': 'follower removed'}, status=status.HTTP_200_OK)
            else:
                return Response({'message': 'follower does not exist'}, status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class InboxView(APIView, PaginationHandlerMixin):
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsRemotePostOnly]
    pagination_class = BasicPagination
    
    def get_serializer(self, request, queryset):
        return InboxSerializer(queryset, many=True, context={'request': request})

    def get(self, request, author_id):
        """Returns the list of inbox items in the order of newest to oldest"""
        author = get_object_or_404(Author, pk=author_id)
        queryset = author.inbox.order_by('-created_at').all()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_paginated_response(
                self.get_serializer(request, page).data
            )
        else:
            serializer = self.get_serializer(request, queryset)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, author_id):
        if 'type' not in request.data:
            return Response({'message': 'must specify the type of inbox'}, status=status.HTTP_400_BAD_REQUEST)
        if request.data['type'] == 'follow':
            return FollowRequestProcessor(request, author_id).get_response()
        elif request.data['type'] == 'post':
            return RemotePostProcessor(request, author_id).get_response()
        elif request.data['type'] == 'like':
            return LikePostProcessor(request, author_id).get_response()
        elif request.data['type'] == 'comment':
            return CommentOnPostProcessor(request, author_id).get_response()
        else:
            return Response({'message': "unknown 'type'"}, status=status.HTTP_400_BAD_REQUEST)


class NodesView(APIView):
    authentication_classes = [BasicAuthentication]
    permission_classes = [permissions.IsAdminUser]
    
    def get(self, request):
        queryset = Author.objects.filter(is_remote_user=True).all()
        serializer = NodesListSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def post(self, request):
        serializer = AddNodeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class NodeDetailView(APIView):
    authentication_classes = [BasicAuthentication]
    permission_classes = [permissions.IsAdminUser]
    
    def delete(self, request, node_id):
        node = get_object_or_404(Author, pk=node_id)
        node.delete()
        return Response({'message': 'node deleted'}, status=status.HTTP_200_OK)
