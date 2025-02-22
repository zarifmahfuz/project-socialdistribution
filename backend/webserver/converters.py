import webserver.models as models
from .utils import (
    join_urls, 
    get_host_from_absolute_url, 
    get_author_id_from_url, 
    get_post_id_from_url,
    format_uuid_without_dashes
)
import logging
from django.http.request import HttpRequest
import webserver.api_client as api_client
import json

logger = logging.getLogger(__name__)

class Converter(object):
    def __init__(self) -> None:
        self.expected_status_codes = {
            "check_for_follower": 200,
            "send_follow_request": 201,
            "send_post_inbox": 201,
        }
    
    def url_to_send_follow_request_at(self, author_url):
        return join_urls(author_url, "inbox", ends_with_slash=True)
    
    def url_to_send_post_inbox_at(self, author_url):
        return join_urls(author_url, "inbox", ends_with_slash=True)
    
    def url_to_send_comment_at(self, author_url, post_id=None):
        return join_urls(author_url, "inbox", ends_with_slash=True)

    def url_to_send_like_at(self, author_url, post_id=None, comment_id=None):
        return join_urls(author_url, "inbox", ends_with_slash=True)
    
    def url_to_get_comments_at(self, author_url, post_id):
        return join_urls(author_url, "posts", post_id, "comments")
    
    def url_to_get_likes_at(self, author_url, post_id, comment_id=None):
        if comment_id is None:
            return join_urls(author_url, "posts", post_id, "likes")
        return join_urls(author_url, "posts", post_id, "comments", comment_id, "likes")

    def url_to_get_author_liked_objects(self, author_url):
        return join_urls(author_url, "liked")

    # returns the request payload required for sending a follow request
    def send_follow_request(self, request_data, request: HttpRequest):
        return request_data
    
    def skip_follow_check_before_sending_follow_request(self):
        return False
    
    def send_comment_inbox(self, request: HttpRequest):
        return request.data
    
    def send_like_inbox(self, request: HttpRequest):
        return request.data
    
    # returns the request payload required for sending a post inbox
    # the passed post is a local post
    def send_post_inbox(self, post, request: HttpRequest):
        payload = {
            "type": "post",
            "post": {
                "id": f"{post.id}",
                "author": {
                    "id": f"{post.author.id}",
                    "url": post.author.get_url(request),
                }
            }
        }
        return payload

    def public_posts_url(self, api_url):
        return join_urls(api_url, "posts", ends_with_slash=True)
    
    def remote_follow_request_sender_id(self, serialized_data):
        id = serialized_data["sender"]["id"]
        if "authors" in id:
            # e.g. "http://127.0.0.1:5454/authors/1d698d25ff008f7538453c120f581471"
            id_section = id.split("authors")[1]
            return id_section.split("/")[0].strip("/")
        return id

    def expected_status_code(self, use_case_name):
        return self.expected_status_codes.get(use_case_name, 200)
    
    # converts a remote author's response to the format specified by AuthorSerializer
    def convert_author(self, data: dict):
        return data
    
    def convert_authors(self, data):
        authors_list = []
        if isinstance(data, list):
            for author in data:
                converted_data = self.convert_author(author)
                if converted_data is not None:
                    authors_list.append(converted_data)
        else:
            # data must be in paginated form
            if "results" in data:
                for author in data["results"]:
                    converted_data = self.convert_author(author)
                    if converted_data is not None:
                        authors_list.append(converted_data)
        return authors_list
    
    # converts a remote post's response to the format specified by PostSerializer
    def convert_post(self, data: dict):
        return data
    
    def convert_posts(self, data, from_public_posts_url=False):
        if isinstance(data, list):
            return [self.convert_post(post) for post in data]
        else:
            # data must be in paginated form
            if "results" in data:
                for i in range(len(data["results"])):
                    data["results"][i] = self.convert_post(data["results"][i])
                return data
        return None
    
    def convert_comment(self, data: dict):
        return data

    def convert_comments(self, data: list):
        if isinstance(data, list):
            return [self.convert_comment(comment) for comment in data]
        else:
            # data must be in paginated form
            if "results" in data:
                return [self.convert_comment(comment) for comment in data["results"]]
        return None
    
    def supports_image_fetch(self):
        return True
    
    def convert_like(self, data: dict):
        return data
    
    def convert_likes(self, data: list):
        if isinstance(data, list):
            return [self.convert_like(like) for like in data]
        else:
            # data must be in paginated form
            if "results" in data:
                return [self.convert_comment(like) for like in data["results"]]
        return None 


class Team11Converter(Converter):
    def skip_follow_check_before_sending_follow_request(self):
        return True
    
    # TODO: Update this when they support comments
    def url_to_send_comment_at(self, author_url, post_id=None):
        return None
    
    def url_to_send_like_at(self, author_url, post_id=None, comment_id=None):
        return None
    
    def url_to_get_comments_at(self, author_url, post_id):
        return join_urls(author_url, "posts", format_uuid_without_dashes(post_id), "comments")
    
    def url_to_get_likes_at(self, author_url, post_id, comment_id=None):
        if comment_id is None:
            return join_urls(author_url, "posts", format_uuid_without_dashes(post_id), "likes")
        return join_urls(
            author_url,
            "posts",
            format_uuid_without_dashes(post_id),
            "comments",
            format_uuid_without_dashes(comment_id),
            "likes"
        )

    def send_follow_request(self, request_data, request: HttpRequest):
        actor = models.Author.objects.get(id=request_data["sender"]["id"])
        host = get_host_from_absolute_url(actor.get_url(request))
        res, _ = api_client.http_request(
            "GET", request_data["receiver"]["url"], node=models.Node.objects.get(team=11),
        )
        payload = {
            "type": "inbox",
            "author": request_data["sender"]["url"],
            "items": [{
                "type": "Follow",
                "actor": {
                    "type": "author",
                    "id": request_data["sender"]["url"],
                    "url": request_data["sender"]["url"],
                    "host": host,
                    "displayName": actor.display_name,
                    "github": actor.github_handle,
                    "profileImage": actor.profile_image
                },
                "object": res
            }]
        }
        logger.info(f"Team 11's send follow request payload: {json.dumps(payload, indent=4)}")
        return payload
    
    def send_post_inbox(self, post, request: HttpRequest):
        host = get_host_from_absolute_url(post.author.get_url(request))
        return {
            "type": "inbox",
            "author": post.author.get_url(request),
            "items": [{
                "type": "post",
                "id": post.get_url(request),
                "title": post.title,
                "source": "www.default.com" if post.source == "" else post.source,
                "origin": "www.default.com" if post.source == "" else post.source,
                "description": post.description,
                "contentType": post.content_type,
                "content": post.content,
                "comments": join_urls(post.get_url(request), "comments"),
                "published": f"{post.created_at}",
                "visibility": post.visibility,
                "unlisted": post.unlisted,
                "categories": [],
                "author": {
                    "type": "author",
                    "id": post.author.get_url(request),
                    "host": host,
                    "displayName": post.author.display_name,
                    "url": post.author.get_url(request),
                    "github": post.author.github_handle,
                    "profileImage": post.author.profile_image
                }
            }]
        }
    
    def public_posts_url(self, api_url):
        return join_urls(api_url, "authors/all/posts")
    
    def convert_author(self, data: dict):
        try:
            return {
                "url": data["url"],
                "id":  get_author_id_from_url(data["id"]),
                "display_name": data["displayName"],
                "profile_image": data["profileImage"],
                "github_handle": data["github"],
            }
        except Exception as e:
            logger.error(f"Error converting author: {e}")
            return None
    
    def convert_post(self, data: dict):
        return {
            "id": get_post_id_from_url(data["id"]),
            "author": self.convert_author(data["author"]),
            "created_at": data["published"],
            "edited_at": None,
            "title": data.get("title", data.get("description", "")),
            "description": data["description"],
            "visibility": data["visibility"],
            "source": data["source"],
            "origin": data["origin"],
            "unlisted": data["unlisted"],
            "content_type": data["contentType"],
            "content": data["content"],
            "likes_count": 0,
            "count": 0,         # TODO: Update this when they support comments
            "comments": "",     # TODO: Update this when they support comments
            "comments_src": {
                "type": "comments",
                "page": 1,
                "size": 0,
                "comments": []
            }
        }

    def convert_posts(self, data, from_public_posts_url=False):
        if isinstance(data, list):
            return [self.convert_post(post) for post in data]
        else:
            # data must be in paginated form
            if "results" in data:
                return [self.convert_post(post) for post in data["results"]]
        return None
    
    def supports_image_fetch(self):
        return False

class Team10Converter(Converter):
    def __init__(self):
        super().__init__()
        self.expected_status_codes["send_follow_request"] = 200
        self.expected_status_codes["send_post_inbox"] = 200
        
    def skip_follow_check_before_sending_follow_request(self):
        return True

    def url_to_send_follow_request_at(self, author_url):
        return join_urls(author_url, "followers", ends_with_slash=True)
    
    def url_to_send_post_inbox_at(self, author_url):
        return join_urls(author_url, "inbox")
    
    def url_to_send_like_at(self, author_url, post_id=None, comment_id=None):
        return self.url_to_send_post_inbox_at(author_url)
    
    # url_to_get_likes_at - no update
    # url_to_get_author_liked_objects - no update
    # send_like_inbox - done
    # convert_like - done
    # convert_likes - no update
    def send_like_inbox(self, request: HttpRequest):
        if "post" in request.data:
            obj = join_urls(request.data["post"]["author"]["url"], "posts", request.data["post"]["id"])
        else:
            obj = request.data["comment_url"]
        return {
            "type": "like",
            "object": obj,
            "actor": request.data["author"]["url"],
        }
    
    def convert_like(self, data: dict):
        converted_like = {
            "author": self.convert_author(data["author"]) if "author" in data else self.convert_author(data),
            "object": data.get("object", "")
        }
        if "comment" in converted_like["object"]:
            converted_like["comment"] = converted_like["object"]
        elif "post" in converted_like["object"]:
            converted_like["post"] = converted_like["object"]
        return converted_like
    
    def convert_likes(self, data: list):
        if isinstance(data, list):
            return [self.convert_like(like) for like in data]
        else:
            return [self.convert_like(like) for like in data["items"]]

    def url_to_send_comment_at(self, author_url, post_id=None):
        return join_urls(author_url, "posts", post_id, "comments")
    
    # url_to_get_comments_at - no update needed
    # send_comment_inbox - done
    # convert_comment - done
    # convert_comments - done
    # convert_post - done
    # send_post_inbox - done
    def send_comment_inbox(self, request: HttpRequest):
        return {
            "comment": request.data["comment"],
            "contentType": request.data.get("content_type", "text/plain"),
            "actor": request.data["author"]["url"],
        }

    def convert_comment(self, data: dict):
        return {
            "author": self.convert_author(data["author"]),
            "comment": data["comment"],
            "content_type": data["contentType"],
            "created_at": data["published"],
            "id": data["url"]
        }
    
    def convert_comments(self, data: list):
        return [self.convert_comment(comment) for comment in data["items"]]

    def public_posts_url(self, api_url):
        return join_urls(api_url, "posts/public", ends_with_slash=True)
    
    def send_follow_request(self, request_data, request: HttpRequest):
        converted_data = {
            "actor": request_data["sender"]["url"]
        }
        return converted_data
    
    def send_post_inbox(self, post, request: HttpRequest):
        host = get_host_from_absolute_url(post.author.get_url(request))
        converted_data = {
            "author":{
                "type": "author",
                "id": f"{post.author.id}",
                "url": post.author.get_url(request),
                "host": host,
                "displayName": f"{post.author.display_name}",
                "github": f"{post.author.github_handle}",
                "profileImage": f"{post.author.profile_image}"
            },
            "type": "post",
            "id": f"{post.id}",
            "url": post.get_url(request),
            "title": post.title,
            "description": post.description,
            "visibility": post.visibility.lower(),
            "source": "www.default.com" if post.source == "" else post.source,
            "origin": "www.default.com" if post.origin == "" else post.origin,
            "contentType": post.content_type,
            "unlisted": post.unlisted,
            "count": post.comment_set.count(),
            "comments": join_urls(post.get_url(request), "comments"),
            "published": f"{post.created_at}",
        }
        
        return converted_data
        
    def convert_author(self, data: dict):
        converted_data ={
            "url": data["url"],
            "id": data["id"],
            "display_name": data["displayName"],
            "profile_image": data["profileImage"],
            "github_handle": data["github"],
        }
        return converted_data

    def convert_authors(self, data):
        if "items" in data:
            return [self.convert_author(author) for author in data["items"]]
        return None
    
    def convert_post(self, data: dict):
        converted_data = {
            "id": data["id"],
            "author":{
                "url": data["author"]["url"],
                "id": data["author"]["id"],
                "display_name": data["author"]["displayName"],
                "profile_image": data["author"]["profileImage"],
                "github_handle": data["author"]["github"]
            },
            "created_at": data["published"],
            "edited_at": None,
            "title": data["title"],
            "description": data["description"],
            "visibility": data["visibility"].upper(),
            "source": data["source"],
            "origin":data["origin"],
            "unlisted":data["unlisted"],
            "content_type": data["contentType"],
            "content": None,
            "likes_count": 0,
            "count": data["count"],
            "comments": data["comments"],
            "comments_src": {
                "type": "comments",
                "page": 1,
                "size": len(data["commentSrc"]),
                "comments": [self.convert_comment(comment) for comment in data["commentSrc"]]
            }
        }
        return converted_data

    def convert_posts(self, data, from_public_posts_url=False):
        if from_public_posts_url:
            return [self.convert_post(post) for post in data]
        if "items" in data:
            return [self.convert_post(post) for post in data["items"]]
        return None
    
    def supports_image_fetch(self):
        return False


class Team16Converter(Converter):
    def __init__(self):
        super().__init__()

    # NOTE: url to retrieve a singular author cannot end with a slash!
    # NOTE: url to retrieve a singular post cannot end with a slash!
    
    def public_posts_url(self, api_url):
        return None
    
    # TODO: team 16 does support this
    def skip_follow_check_before_sending_follow_request(self):
        return True
    
    # TODO: Update this when they support comments
    def url_to_send_comment_at(self, author_url, post_id=None):
        return None
    
    def url_to_send_like_at(self, author_url, post_id=None, comment_id=None):
        return None
    
    def send_follow_request(self, request_data, request: HttpRequest):
        return {
            "id": request_data["sender"]["url"].strip("/") if request_data["sender"]["url"].endswith("/") \
                else request_data["sender"]["url"],
            "type": "follow"
        }

    def send_post_inbox(self, post, request: HttpRequest):
        host = get_host_from_absolute_url(post.author.get_url(request))
        return {
            "type": "post",
            "data": {
                "author": {
                    "type": "author",
                    "id": post.author.get_url(request),
                    "url": post.author.get_url(request),
                    "host": host,
                    "displayName": post.author.display_name,
                    "github": post.author.github_handle,
                    "profileImage": post.author.profile_image
                },
                "id": post.get_url(request),
                "type": "post",
                "title": post.title,
                "source": post.source,
                "origin": post.origin,
                "description": post.description,
                "contentType": post.content_type,
                "content": post.content,
                "published": f"{post.created_at}",
                "visibility": post.visibility,
                "unlisted": post.unlisted,
            }
        }

    def convert_author(self, data: dict):
        return {
            "url": data["url"],
            "id": get_author_id_from_url(data["id"]),
            "display_name": data["displayName"],
            "profile_image": data["profileImage"],
            "github_handle": data["github"],
        }

    def convert_authors(self, data):
        if "items" in data:
            return [self.convert_author(author) for author in data["items"]]
        return None

    def convert_post(self, data: dict):
        return {
            "id": data["id"],
            "author": self.convert_author(data["author"]),
            "created_at": data["published"],
            "edited_at": None,
            "title": data["title"],
            "description": data["description"],
            "visibility": data["visibility"],
            "source": data["source"],
            "origin": data["origin"],
            "unlisted":data["unlisted"],
            "content_type": data["contentType"],
            "content": data["content"],
            "likes_count": 0
        }

    def convert_posts(self,data, from_public_posts_url=False):
        if "items" in data:
            return [self.convert_post(post) for post in data["items"]]
        return None
    
    def supports_image_fetch(self):
        return False
