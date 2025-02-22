from django.test import TestCase
from webserver.models import Author, FollowRequest, Inbox, Follow, Post, Node, RemoteAuthor, RemotePost, Like
from rest_framework.test import APITestCase
from rest_framework import status
from unittest import mock, skip
import datetime
import json
import uuid
from django.utils.timezone import utc
from responses import matchers
import responses    # https://pypi.org/project/responses/#basics
from unittest.mock import patch
from unittest.mock import Mock
import unittest


class AuthorsViewTestCase(APITestCase):
    def test_get(self):
        # create some authors
        Author.objects.create(username="author_1", display_name="author_1")
        Author.objects.create(username="author_2", display_name="author_2")
        Author.objects.create(username="author_3", display_name="author_3")
        
        url = "/api/authors/"
        self.client.force_authenticate(user=mock.Mock())
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)
        author_1 = response.data[0]
        self.assertEqual(author_1["display_name"], "author_1")
    
    def test_get_does_not_return_admin_and_remote_users(self):
        Author.objects.create(username="admin", display_name="admin", is_admin=True)
        Author.objects.create(username="nodeA", display_name="nodeA", is_remote_user=True)
        regular_author = Author.objects.create(username="regular_author", display_name="regular_author")
        self.assertEqual(3, Author.objects.count())

        url = "/api/authors/"
        self.client.force_authenticate(user=mock.Mock())
        response = self.client.get(url)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(1, len(response.data))
        self.assertEqual(str(regular_author.id), response.data[0]["id"])

    @responses.activate
    def test_get_fetches_remote_authors_for_team14(self):
        node_user_1 = Author.objects.create(username="node_user_1", display_name="node_user_1", 
                                            password="password-team14", is_remote_user=True)
        Node.objects.create(api_url="https://social-distribution-1.herokuapp.com/api", user=node_user_1,
                            auth_username="team14", auth_password="password-team14")
        local_author = Author.objects.create(username="local_author", display_name="local_author")
        
        external_api_response = responses.Response(
            method="GET",
            url="https://social-distribution-1.herokuapp.com/api/authors",
            json=[{
                "url": "https://social-distribution-1.herokuapp.com/api/authors/1/",
                "id": str(uuid.uuid4()),
                "display_name": "casey",
                "profile_image": "",
                "github_handle": "",
            }],
            status=200,
        )
        responses.add(external_api_response)
        
        self.client.force_authenticate(user=local_author)
        url = "/api/authors/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(2, len(response.data))
        author_1 = response.data[0]
        author_2 = response.data[1]
        self.assertEqual("local_author", author_1["display_name"])
        self.assertEqual("casey", author_2["display_name"])
    
    @responses.activate
    def test_get_fetches_remote_authors_for_team10(self):
        node_user_1 = Author.objects.create(username="node_user_1", display_name="node_user_1", 
                                            password="password-team10", is_remote_user=True)
        Node.objects.create(api_url="https://social-distribution-1.herokuapp.com/api", user=node_user_1,
                            auth_username="team10", auth_password="password-team10", team=10)
        local_author = Author.objects.create(username="local_author", display_name="local_author")
        
        external_api_response = responses.Response(
            method="GET",
            url="https://social-distribution-1.herokuapp.com/api/authors",
            json={
                "type":"string",
                "items": [
                    {   
                        "type":"string",
                        "url": "https://social-distribution-1.herokuapp.com/api/authors/1/",
                        "host":"string",
                        "id": str(uuid.uuid4()),
                        "displayName": "casey",
                        "profileImage": "",
                        "github": "",
                    } 
                ]
            },
            status=200,
        )
        responses.add(external_api_response)
        
        self.client.force_authenticate(user=local_author)
        url = "/api/authors/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(2, len(response.data))
        author_1 = response.data[0]
        author_2 = response.data[1]
        self.assertEqual("local_author", author_1["display_name"])
        self.assertEqual("casey", author_2["display_name"])
    
    @responses.activate
    def test_get_fetches_remote_authors_for_team16(self):
        node_user_1 = Author.objects.create(username="node_user_1", display_name="node_user_1", 
                                            password="password-team16", is_remote_user=True)
        Node.objects.create(api_url="https://social-distribution-1.herokuapp.com/api", user=node_user_1,
                            auth_username="team16", auth_password="password-team16", team=16)
        local_author = Author.objects.create(username="local_author", display_name="local_author")
        remote_author_id = str(uuid.uuid4())
        external_api_response = responses.Response(
            method="GET",
            url="https://social-distribution-1.herokuapp.com/api/authors",
            json={
                "type":"string",
                "items": [
                    {   
                        "type":"string",
                        "url": f"https://social-distribution-1.herokuapp.com/api/authors/{remote_author_id}",
                        "host":"string",
                        "id": f"https://social-distribution-1.herokuapp.com/api/authors/{remote_author_id}",
                        "displayName": "casey",
                        "profileImage": "",
                        "github": "",
                    } 
                ]
            },
            status=200,
        )
        responses.add(external_api_response)
        
        self.client.force_authenticate(user=local_author)
        url = "/api/authors/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(2, len(response.data))
        author_1 = response.data[0]
        author_2 = response.data[1]
        self.assertEqual("local_author", author_1["display_name"])
        self.assertEqual("casey", author_2["display_name"])
    
    @responses.activate
    def test_get_can_combine_remote_data_with_local_pagination(self):
        node_user_1 = Author.objects.create(username="node_user_1", display_name="node_user_1", 
                                            password="password-team14", is_remote_user=True)
        Node.objects.create(api_url="https://social-distribution-1.herokuapp.com/api", user=node_user_1,
                            auth_username="team14", auth_password="password-team14")
        local_author = Author.objects.create(username="local_author", display_name="local_author")
        
        external_api_response = responses.Response(
            method="GET",
            url="https://social-distribution-1.herokuapp.com/api/authors",
            json=[{
                "url": "https://social-distribution-1.herokuapp.com/api/authors/1/",
                "id": 1,
                "display_name": "casey",
                "profile_image": "",
                "github_handle": "",
            }],
            status=200,
        )
        responses.add(external_api_response)

        self.client.force_authenticate(user=local_author)
        url = "/api/authors/?page=1"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(2, len(response.data["results"]))
        author_1 = response.data["results"][0]
        author_2 = response.data["results"][1]
        self.assertEqual("local_author", author_1["display_name"])
        self.assertEqual("casey", author_2["display_name"])


class PaginationTestCase(APITestCase):
    def setUp(self):
        self.default_page_size = 10

    def test_pagination_for_multiple_authors_set(self):
        authors_count = 20
        for i in range(0, authors_count):
            username = f'author_{i}'
            display_name = f'author_{i}_handle'
            Author.objects.create(username=username, display_name=display_name)
        
        url = "/api/authors/?page=1"
        self.client.force_authenticate(user=mock.Mock())
        response = self.client.get(url)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertTrue("count" in response.data)
        self.assertTrue("next" in response.data)
        self.assertTrue("previous" in response.data)
        self.assertTrue("results" in response.data)
        self.assertEqual(authors_count, response.data["count"])
        self.assertEqual(self.default_page_size, len(response.data["results"]))
        self.assertEqual("author_0_handle", response.data["results"][0]["display_name"])
    
    def test_pagination_for_empty_authors_set(self):
        url = "/api/authors/?page=1"
        self.client.force_authenticate(user=mock.Mock())
        response = self.client.get(url)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(0, response.data["count"])
        self.assertEqual(0, len(response.data["results"]))
        self.assertIsNone(response.data["previous"])
        self.assertIsNone(response.data["next"])
    
    def test_pagination_page_size(self):
        authors_count = 20
        for i in range(0, authors_count):
            username = f'author_{i}'
            display_name = f'author_{i}_handle'
            Author.objects.create(username=username, display_name=display_name)
        
        page_size = authors_count
        url = f'/api/authors/?page=1&size={page_size}'
        self.client.force_authenticate(user=mock.Mock())
        response = self.client.get(url)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(page_size, len(response.data["results"]))
        self.assertIsNone(response.data["previous"])
        self.assertIsNone(response.data["next"])
    
    def test_pagination_next(self):
        authors_count = 20
        for i in range(0, authors_count):
            username = f'author_{i}'
            display_name = f'author_{i}_handle'
            Author.objects.create(username=username, display_name=display_name)

        url = "/api/authors/?page=1"
        self.client.force_authenticate(user=mock.Mock())
        response = self.client.get(url)
        self.assertEqual(status.HTTP_200_OK, response.status_code)

        self.assertEqual(self.default_page_size, len(response.data["results"]))
        self.assertEqual("http://testserver/api/authors/?page=2", response.data["next"])
        self.assertEqual("author_0_handle", response.data["results"][0]["display_name"])

        response_next = self.client.get(response.data["next"])
        self.assertEqual(status.HTTP_200_OK, response_next.status_code)
        self.assertEqual(self.default_page_size, len(response_next.data["results"]))
        self.assertEqual("author_10_handle", response_next.data["results"][0]["display_name"])
    
    def test_pagination_prev(self):
        authors_count = 20
        for i in range(0, authors_count):
            username = f'author_{i}'
            display_name = f'author_{i}_handle'
            Author.objects.create(username=username, display_name=display_name)
        
        url = "/api/authors/?page=2&size=10"
        self.client.force_authenticate(user=mock.Mock())
        response = self.client.get(url)
        self.assertEqual(status.HTTP_200_OK, response.status_code)

        self.assertEqual(self.default_page_size, len(response.data["results"]))
        self.assertEqual("author_10_handle", response.data["results"][0]["display_name"])

        response_previous = self.client.get(response.data["previous"])
        self.assertEqual(status.HTTP_200_OK, response_previous.status_code)
        self.assertEqual(self.default_page_size, len(response_previous.data["results"]))
        self.assertEqual("author_0_handle", response_previous.data["results"][0]["display_name"])


class AuthorDetailView(APITestCase):
    def test_get(self):
        author_1 = Author.objects.create(username="author_1", display_name="author_1")
        url = f'/api/authors/{author_1.id}/'
        self.client.force_authenticate(user=mock.Mock())
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["display_name"], "author_1")
    
    @responses.activate
    def test_get_remote_author(self):
        local_author = Author.objects.create(username="local_author", display_name="local_author")
        node_user = Author.objects.create(username="node_user", display_name="node_user", is_remote_user=True)
        node = Node.objects.create(api_url="https://social-distribution-1.herokuapp.com/api", user=node_user,
                                   auth_username="team14", auth_password="password-team14", team=14)
        remote_author = RemoteAuthor.objects.create(id=uuid.uuid4(), node=node)
        
        remote_author_json = {
            "url": f"https://social-distribution-1.herokuapp.com/api/authors/{remote_author.id}/",
            "id": f"{remote_author.id}",
            "display_name": "Jake",
            "profile_image": "",
            "github_handle": ""
        }
        responses.add(
            responses.GET,
            f"https://social-distribution-1.herokuapp.com/api/authors/{remote_author.id}",
            json=remote_author_json,
            status=200,
        )

        url = f'/api/authors/{remote_author.id}/'
        self.client.force_authenticate(user=local_author)
        response = self.client.get(url)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(remote_author_json, response.data)
    
    @responses.activate
    def test_get_remote_author_team_10(self):
        local_author = Author.objects.create(username="local_author", display_name="local_author")
        node_user = Author.objects.create(username="node_user", display_name="node_user", is_remote_user=True)
        node = Node.objects.create(api_url="https://social-distribution-1.herokuapp.com/api", user=node_user,
                                   auth_username="team10", auth_password="password-team10", team=10)
        remote_author = RemoteAuthor.objects.create(id=uuid.uuid4(), node=node)
        
        remote_author_json = {
            "type":"author",
            "url": f"https://social-distribution-1.herokuapp.com/api/authors/{remote_author.id}/",
            "id": f"{remote_author.id}",
            "host":"host",
            "displayName": "Jake",
            "profileImage": "",
            "github": ""
        }
        responses.add(
            responses.GET,
            f"https://social-distribution-1.herokuapp.com/api/authors/{remote_author.id}",
            json=remote_author_json,
            status=200,
        )

        url = f'/api/authors/{remote_author.id}/'
        self.client.force_authenticate(user=local_author)
        response = self.client.get(url)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        remote_author_converted = {
            "url": f"https://social-distribution-1.herokuapp.com/api/authors/{remote_author.id}/",
            "id": f"{remote_author.id}",
            "display_name": "Jake",
            "profile_image": "",
            "github_handle": ""
        }
        self.assertEqual(remote_author_converted, response.data)

    @responses.activate
    def test_get_remote_author_team_16(self):
        local_author = Author.objects.create(username="local_author", display_name="local_author")
        node_user = Author.objects.create(username="node_user", display_name="node_user", is_remote_user=True)
        node = Node.objects.create(api_url="https://social-distribution-1.herokuapp.com/api", user=node_user,
                                   auth_username="team16", auth_password="password-team16", team=16)
        remote_author = RemoteAuthor.objects.create(id=uuid.uuid4(), node=node)
        
        remote_author_json = {
            "type":"author",
            "url": f"https://social-distribution-1.herokuapp.com/api/authors/{remote_author.id}/",
            "id": f"https://social-distribution-1.herokuapp.com/api/authors/{remote_author.id}/",
            "host":"host",
            "displayName": "Jake",
            "profileImage": "",
            "github": ""
        }
        responses.add(
            responses.GET,
            f"https://social-distribution-1.herokuapp.com/api/authors/{remote_author.id}",
            json=remote_author_json,
            status=200,
        )

        url = f'/api/authors/{remote_author.id}/'
        self.client.force_authenticate(user=local_author)
        response = self.client.get(url)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        remote_author_converted = {
            "url": f"https://social-distribution-1.herokuapp.com/api/authors/{remote_author.id}/",
            "id": f"{remote_author.id}",
            "display_name": "Jake",
            "profile_image": "",
            "github_handle": ""
        }
        self.assertEqual(remote_author_converted, response.data)

    def test_get_404(self):
        """If an author requested does not exist, should return 404"""
        fake_id = uuid.uuid4()
        url = f'/api/authors/{fake_id}/'
        self.client.force_authenticate(user=mock.Mock())
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        
    
    def test_post_all_fields(self):
        """POST request works on all editable data fields"""
        author_1 = Author.objects.create()
        url = f'/api/authors/{author_1.id}/'
        self.client.force_authenticate(user=author_1)
        payload = {
            "display_name": "Mark McGoey",
            "profile_image": "No image",
            "github_handle": "mmcgoey"
        }
        response = self.client.post(url,data=payload)
        self.assertEqual(response.data["display_name"], "Mark McGoey")
        self.assertEqual(response.data["profile_image"], "No image")
        self.assertEqual(response.data["github_handle"], "mmcgoey")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    
    
    def test_post_no_fields(self):
        author_1 = Author.objects.create()
        url = f'/api/authors/{author_1.id}/'
        self.client.force_authenticate(user=author_1)
        payload = {}
        response = self.client.post(url,data=payload)
        self.assertEqual(response.data["display_name"], "")
        self.assertEqual(response.data["profile_image"], "")
        self.assertEqual(response.data["github_handle"], "")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    
    def test_partial_post(self):
        """POST request can handle partial update"""
        author_1 = Author.objects.create()
        url = f'/api/authors/{author_1.id}/'
        payload = {
            "display_name": "Mark McGoey",
            "github_handle": "mmcgoey"
        }
        self.client.force_authenticate(user=author_1)
        response = self.client.post(url,data=payload)
        self.assertEqual(response.data["display_name"], "Mark McGoey")
        self.assertEqual(response.data["profile_image"], "")
        self.assertEqual(response.data["github_handle"], "mmcgoey")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        
    
    def test_post_404(self):
        """If an author to be updated does not exist, should return 404"""
        fake_id = uuid.uuid4()
        url = f'/api/authors/{fake_id}/'
        payload = {
            "display_name": "Mark McGoey",
            "profile_image": "No image",
            "github_handle": "mmcgoey"
        }
        self.client.force_authenticate(user=Author.objects.create())
        response = self.client.post(url,data=payload)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_post_non_editable_fields(self):
        author_1 = Author.objects.create()
        url = f'/api/authors/{author_1.id}/'
        new_id = uuid.uuid4()
        new_url = f'/api/authors/{new_id}/'
        payload = {
            "id":new_id,
            "url":new_url
        }
        self.client.force_authenticate(user=author_1)
        response = self.client.post(url,data=payload)
        
        self.assertEqual(response.data["id"], str(author_1.id))
        self.assertEqual(response.data["url"],'http://testserver'+url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class AuthorRegistrationTestCase(APITestCase):
    def test_register_successful(self):
        request_payload = {
            "username": "author_1",
            "display_name": "best_author",
            "password": "password",
            "password2": "password"
        }
        response = self.client.post("/api/register/", data=request_payload, format="json")
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        self.assertEqual("best_author", response.data["display_name"])
    
    def test_register_with_duplicate_username(self):
        Author.objects.create(username="author_1", display_name="author_1")
        request_payload = {
            "username": "author_1",
            "display_name": "best_author",
            "password": "password",
            "password2": "password"
        }
        response = self.client.post("/api/register/", data=request_payload, format="json")
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)
    
    def test_register_with_mismatched_passwords(self):
        request_payload = {
            "username": "author_1",
            "display_name": "best_author",
            "password": "password",
            "password2": "other password"
        }
        response = self.client.post("/api/register/", data=request_payload, format="json")
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)
    
    def test_register_with_incomplete_data(self):
        # password2 missing
        request_payload = {
            "username": "author_1",
            "display_name": "best_author",
            "password": "password"
        }
        response = self.client.post("/api/register/", data=request_payload, format="json")
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)


class LoginTestCase(APITestCase):
    def test_login_with_valid_credentials(self):
        author = Author.objects.create(username="author_1", display_name="author_1")
        author.set_password("pass123")
        author.save()

        request_payload = {"username": "author_1", "password": "pass123"}
        response = self.client.post("/api/login/", data=request_payload, format="json")
        self.assertEqual(status.HTTP_200_OK, response.status_code)
    
    def test_login_with_invalid_credentials(self):
        request_payload = {"username": "author_1", "password": "pass123"}
        response = self.client.post("/api/login/", data=request_payload, format="json")
        self.assertEqual(status.HTTP_401_UNAUTHORIZED, response.status_code)
    
    def test_login_with_incomplete_request_payload(self):
        request_payload = {"username": "author_1"}
        response = self.client.post("/api/login/", data=request_payload, format="json")
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)


class LogoutTestCase(APITestCase):
    def test_logout(self):
        """Always logs out a request"""
        response = self.client.post("/api/logout/")
        self.assertEqual(status.HTTP_200_OK, response.status_code)


class FollowRequestProcessorTestCase(APITestCase):
    def setUp(self):
        self.resource_name = "follow-requests"

    def test_create_follow_request_and_update_inbox(self):
        author_1 = Author.objects.create(username="author_1", display_name="author_1")
        author_2 = Author.objects.create(username="author_2", display_name="author_2")
        payload = {
            "type": "follow",
            "sender": {
                "url": f'http://127.0.0.1:5054/authors/{author_1.id}/',
                "id": author_1.id,
            },
            "receiver": {
                "url": f'http://127.0.0.1:5054/authors/{author_2.id}/',
                "id": author_2.id,
            }
        }
        self.assertEqual(0, FollowRequest.objects.count())
        url = f'/api/authors/{author_2.id}/inbox/'
        self.client.force_authenticate(user=mock.Mock())
        response = self.client.post(url, data=payload, format="json")

        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        self.assertEqual(1, FollowRequest.objects.count())
        fr = FollowRequest.objects.first()
        self.assertEqual(author_1, fr.sender)
        self.assertEqual(author_2, fr.receiver)

        self.assertEqual(1, Inbox.objects.count())
        inbox = Inbox.objects.first()
        self.assertEqual(author_2, inbox.target_author)
        self.assertEqual(fr, inbox.follow_request_received)
    
    def test_duplicate_follow_request_is_not_allowed(self):
        """It should raise an error when you try to create a follow request that already exists"""
        author_1 = Author.objects.create(username="author_1", display_name="author_1")
        author_2 = Author.objects.create(username="author_2", display_name="author_2")
        FollowRequest.objects.create(sender=author_1, receiver=author_2)
        self.assertEqual(1, FollowRequest.objects.count())

        payload = {
            "type": "follow",
            "sender": {
                "url": f'http://127.0.0.1:5054/authors/{author_1.id}',
                "id": author_1.id,
            },
            "receiver": {
                "url": f'http://127.0.0.1:5054/authors/{author_2.id}',
                "id": author_2.id,
            }
        }
        url = f'/api/authors/{author_2.id}/inbox/'
        self.client.force_authenticate(user=mock.Mock())
        response = self.client.post(url, data=payload, format="json")
        self.assertEqual(status.HTTP_409_CONFLICT, response.status_code)
        self.assertEqual(1, FollowRequest.objects.count())
        
    def test_reverse_follow_request_is_allowed(self):
        """Author 1 can send a follow request to Author 2 and Author 2 can send a follow request to Author 1"""
        author_1 = Author.objects.create(username="author_1", display_name="author_1")
        author_2 = Author.objects.create(username="author_2", display_name="author_2")
        FollowRequest.objects.create(sender=author_1, receiver=author_2)
        self.assertEqual(1, FollowRequest.objects.count())
        
        payload = {
            "type": "follow",
            "sender": {
                "url": f'http://127.0.0.1:5054/authors/{author_2.id}',
                "id": author_2.id,
            },
            "receiver": {
                "url": f'http://127.0.0.1:5054/authors/{author_1.id}',
                "id": author_1.id,
            }
        }
        url = f'/api/authors/{author_1.id}/inbox/'
        self.client.force_authenticate(user=mock.Mock())
        response = self.client.post(url, data=payload, format="json")
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        self.assertEqual(2, FollowRequest.objects.count())
        fr = FollowRequest.objects.get(sender=author_2, receiver=author_1)
        self.assertEqual(author_2, fr.sender)
        self.assertEqual(author_1, fr.receiver)

    def test_cannot_send_follow_request_to_self(self):
        """Author cannot send follow request to themselves"""
        author_1 = Author.objects.create(username="author_1", display_name="author_1")
        author_2 = Author.objects.create(username="author_2", display_name="author_2")
        self.assertEqual(0, FollowRequest.objects.count())
        payload = {
            "sender": {
                "url": f'http://127.0.0.1:5054/authors/{author_1.id}',
                "id": author_1.id,
            },
            "receiver": {
                "url": f'http://127.0.0.1:5054/authors/{author_1.id}',
                "id": author_1.id,
            }
        }
        url = f'/api/authors/{author_1.id}/inbox/'
        self.client.force_authenticate(user=mock.Mock())
        response = self.client.post(url, data=payload, format="json")
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)
        self.assertEqual(0, FollowRequest.objects.count())
    
    def test_request_not_valid_when_required_fields_are_not_given(self):
        """Proper serializer fields need to be given"""
        author_1 = Author.objects.create(username="author_1", display_name="author_1")
        author_2 = Author.objects.create(username="author_2", display_name="author_2")
        # 'url' field is missing in the sender
        payload = {
            "type": "follow",
            "sender": {
                "id": author_1.id,
            },
            "receiver": {
                "url": f'http://127.0.0.1:5054/authors/{author_1.id}',
                "id": author_1.id,
            }
        }
        url = f'/api/authors/{author_1.id}/inbox/'
        self.client.force_authenticate(user=mock.Mock())
        response = self.client.post(url, data=payload, format="json")
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)
        self.assertEqual(0, FollowRequest.objects.count())

    def test_request_is_valid_when_extra_fields_are_given(self):
        author_1 = Author.objects.create(username="author_1", display_name="author_1")
        author_2 = Author.objects.create(username="author_2", display_name="author_2")
        self.assertEqual(0, FollowRequest.objects.count())
        payload = {
            "type": "follow",
            "sender": {
                "url": f'http://127.0.0.1:5054/authors/{author_1.id}',
                "id": author_1.id,
                "display_name": "author_1",
                "profile_image": "",
                "github_handle": ""
            },
            "receiver": {
                "url": f'http://127.0.0.1:5054/authors/{author_2.id}',
                "id": author_2.id,
                "display_name": "author_2",
                "profile_image": "",
                "github_handle": ""
            }
        }
        
        url = f'/api/authors/{author_2.id}/inbox/'
        self.client.force_authenticate(user=mock.Mock())
        response = self.client.post(url, data=payload, format="json")

        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        self.assertEqual(1, FollowRequest.objects.count())
        fr = FollowRequest.objects.first()
        self.assertEqual(author_1, fr.sender)
        self.assertEqual(author_2, fr.receiver)
    
    def test_cannot_send_follow_request_if_already_a_follower(self):
        """Cannot send a follow request to someone who's already being followed"""
        author_1 = Author.objects.create(username="author_1", display_name="author_1")
        author_2 = Author.objects.create(username="author_2", display_name="author_2")
        Follow.objects.create(follower=author_1, followee=author_2)
        self.assertEqual(1, Follow.objects.count())

        payload = {
            "type": "follow",
            "sender": {
                "url": f'http://127.0.0.1:5054/authors/{author_1.id}',
                "id": author_1.id,
            },
            "receiver": {
                "url": f'http://127.0.0.1:5054/authors/{author_2.id}',
                "id": author_2.id,
            }
        }
        url = f'/api/authors/{author_2.id}/inbox/'
        self.client.force_authenticate(user=mock.Mock())
        response = self.client.post(url, data=payload, format="json")
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)
        self.assertEqual(0, FollowRequest.objects.count())

    @responses.activate
    def test_receiver_is_remote_author_for_team14(self):
        local_author = Author.objects.create(username="local_author", display_name="local_author")
        node_user_1 = Author.objects.create(username="node_user_1", display_name="node_user_1", 
                                            password="password1", is_remote_user=True)
        Node.objects.create(api_url="https://social-distribution-1.herokuapp.com/api", user=node_user_1,
                            auth_username="team14", auth_password="password-team14", team=14)
        remote_author_id = uuid.uuid4()
        payload = {
            "type": "follow",
            "sender": {
                "url": f'http://127.0.0.1:5054/authors/{local_author.id}/',
                "id": str(local_author.id),
            },
            "receiver": {
                "url": f'https://social-distribution-1.herokuapp.com/api/authors/{remote_author_id}/',
                "id": str(remote_author_id),
            }
        }
        
        responses.add(
            responses.GET,
            f"https://social-distribution-1.herokuapp.com/api/authors/{remote_author_id}/followers/{local_author.id}",
            status=404, # local author does not follow remote author yet
        )
        responses.add(
            responses.POST,
            f"https://social-distribution-1.herokuapp.com/api/authors/{remote_author_id}/inbox/",
            match=[
                matchers.json_params_matcher(payload),  # team 14's follow request payload
            ],
            status=201,
        )
        
        url = f'/api/authors/{remote_author_id}/inbox/'
        self.client.force_authenticate(user=local_author)
        response = self.client.post(url, data=payload, format="json")
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        # shouldn't create a local FR object for a remote receiver
        self.assertEqual(0, FollowRequest.objects.count())
    
    @unittest.skip
    @responses.activate
    def test_receiver_is_remote_author_for_team11(self):
        local_author = Author.objects.create(username="local_author", display_name="local_author")
        node_user_1 = Author.objects.create(username="node_user_1", display_name="node_user_1", 
                                            password="password1", is_remote_user=True)
        Node.objects.create(api_url="https://social-distribution-1.herokuapp.com/api", user=node_user_1,
                            auth_username="team11", auth_password="password-team11", team=11)
        remote_author_id = uuid.uuid4()
        payload = {
            "type": "follow",
            "sender": {
                "url": f'http://testserver.com/api/authors/{local_author.id}/',
                "id": str(local_author.id),
            },
            "receiver": {
                "url": f'https://social-distribution-1.herokuapp.com/api/authors/{remote_author_id}/',
                "id": str(remote_author_id),
            }
        }
        
        responses.add(
            responses.GET,
            f"https://social-distribution-1.herokuapp.com/api/authors/{remote_author_id}/followers/{local_author.id}",
            status=404, # local author does not follow remote author yet
        )
        remote_author_json = {
            "type": "author",
            "id": f"https://social-distribution-1.herokuapp.com/api/authors/{remote_author_id}",
            "host": "https://social-distribution-1.herokuapp.com/api",
            "displayName": "test_user",
            "url": f"https://social-distribution-1.herokuapp.com/api/authors/{remote_author_id}",
            "github": "",
            "profileImage": "https://cdn.pixabay.com/photo/2015/10/05/22/37/blank-profile-picture-973460_1280.png"
        }
        responses.add(
            responses.GET,
            f"https://social-distribution-1.herokuapp.com/api/authors/{remote_author_id}/",
            json=remote_author_json,
            status=200,
        )
        
        expected_payload = {
            "type": "inbox",
            "author": f'https://social-distribution-1.herokuapp.com/api/authors/{remote_author_id}/',
            "items": [{
                "type": "Follow",
                "actor": {
                    "type": "author",
                    "id": f"http://testserver.com/api/authors/{local_author.id}/",
                    "host": "http://testserver/",
                    "displayName": local_author.display_name,
                    "github": local_author.github_handle,
                    "url": f"http://testserver.com/api/authors/{local_author.id}/",
                    "profileImage": local_author.profile_image,
                },
                "object": remote_author_json,
            }]
        }

        responses.add(
            responses.POST,
            f"https://social-distribution-1.herokuapp.com/api/authors/{remote_author_id}/inbox/",
            match=[
                matchers.json_params_matcher(expected_payload),  # team 11's follow request payload
            ],
            status=201,
        )
        
        url = f'/api/authors/{remote_author_id}/inbox/'
        self.client.force_authenticate(user=local_author)
        response = self.client.post(url, data=payload, format="json")
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        # shouldn't create a local FR object for a remote receiver
        self.assertEqual(0, FollowRequest.objects.count())
    
    @responses.activate
    def test_receiver_is_remote_author_for_team10(self):
        local_author = Author.objects.create(username="local_author", display_name="local_author")
        node_user_1 = Author.objects.create(username="node_user_1", display_name="node_user_1", 
                                            password="password1", is_remote_user=True)
        Node.objects.create(api_url="https://social-distribution-1.herokuapp.com/api", user=node_user_1,
                            auth_username="team10", auth_password="password-team10", team=10)
        remote_author_id = uuid.uuid4()
        remote_payload = {
            "actor": f'http://127.0.0.1:5054/authors/{local_author.id}/'
        }
        responses.add(
            responses.GET,
            f"https://social-distribution-1.herokuapp.com/api/authors/{remote_author_id}/followers/{local_author.id}",
            status=404, # local author does not follow remote author yet
        )
        responses.add(
            responses.POST,
            f"https://social-distribution-1.herokuapp.com/api/authors/{remote_author_id}/followers/",
            match=[
                matchers.json_params_matcher(remote_payload),  # team 10's follow request payload
            ],
            status=200,
        )
        local_payload = {
            "type":"follow",
            "sender":{
                "url":f'http://127.0.0.1:5054/authors/{local_author.id}/',
                "id": str(local_author.id)
            },
            "receiver":{
                "url": f"https://social-distribution-1.herokuapp.com/api/authors/{remote_author_id}/",
                "id": str(remote_author_id)
            }
        }
        
        url = f'/api/authors/{remote_author_id}/inbox/'
        self.client.force_authenticate(user=local_author)
        response = self.client.post(url, data=local_payload, format="json")
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        # shouldn't create a local FR object for a remote receiver
        self.assertEqual(0, FollowRequest.objects.count())

    @responses.activate
    def test_receiver_is_remote_author_for_team16(self):
        local_author = Author.objects.create(username="local_author", display_name="local_author")
        node_user_1 = Author.objects.create(username="node_user_1", display_name="node_user_1", 
                                            password="password1", is_remote_user=True)
        Node.objects.create(api_url="https://social-distribution-1.herokuapp.com/api", user=node_user_1,
                            auth_username="team16", auth_password="password-team16", team=16)
        remote_author_id = uuid.uuid4()
        remote_payload = {
            "id": f'http://127.0.0.1:5054/authors/{local_author.id}',
            "type": "follow"
        }
        responses.add(
            responses.GET,
            f"https://social-distribution-1.herokuapp.com/api/authors/{remote_author_id}/followers/{local_author.id}",
            status=404, # local author does not follow remote author yet
        )
        responses.add(
            responses.POST,
            f"https://social-distribution-1.herokuapp.com/api/authors/{remote_author_id}/inbox/",
            match=[
                matchers.json_params_matcher(remote_payload),  # team 16's follow request payload
            ],
            status=201,
        )
        local_payload = {
            "type":"follow",
            "sender":{
                "url":f'http://127.0.0.1:5054/authors/{local_author.id}/',
                "id": str(local_author.id)
            },
            "receiver":{
                "url": f"https://social-distribution-1.herokuapp.com/api/authors/{remote_author_id}/",
                "id": str(remote_author_id)
            }
        }
        
        url = f'/api/authors/{remote_author_id}/inbox/'
        self.client.force_authenticate(user=local_author)
        response = self.client.post(url, data=local_payload, format="json")
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        # shouldn't create a local FR object for a remote receiver
        self.assertEqual(0, FollowRequest.objects.count())


    def test_sender_is_remote_author(self):
        local_author = Author.objects.create(username="local_author", display_name="local_author")
        node_user_1 = Author.objects.create(username="node_user_1", display_name="node_user_1", 
                                            password="password1", is_remote_user=True)
        Node.objects.create(api_url="https://social-distribution-1.herokuapp.com/api", user=node_user_1,
                            auth_username="team14", auth_password="password-team14", team=14)
        remote_author_id = uuid.uuid4()
        payload = {
            "type": "follow",
            "sender": {
                "url": f'https://social-distribution-1.herokuapp.com/api/authors/{remote_author_id}/',
                "id": str(remote_author_id),
            },
            "receiver": {
                "url": f'http://127.0.0.1:5054/authors/{local_author.id}/',
                "id": str(local_author.id),
            }
        }
        self.assertEqual(0, FollowRequest.objects.count())
        self.assertEqual(0, Inbox.objects.count())
        
        url = f'/api/authors/{local_author.id}/inbox/'
        self.client.force_authenticate(user=local_author)
        response = self.client.post(url, data=payload, format="json")
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        self.assertEqual(1, FollowRequest.objects.count())
        self.assertEqual(1, Inbox.objects.count())
        fr = FollowRequest.objects.first()
        self.assertEqual(remote_author_id, fr.remote_sender.id)
        self.assertEqual(local_author, fr.receiver)
        inbox = Inbox.objects.first()
        self.assertEqual(fr, inbox.follow_request_received)
        self.assertEqual(local_author, inbox.target_author)


class FollowRequestsTestCase(APITestCase):
    def setUp(self):
        self.resource_name = "follow-requests"
    
    def test_author_has_multiple_follow_requests(self):
        author_1 = Author.objects.create(username="author_1", display_name="author_1")
        author_2 = Author.objects.create(username="author_2", display_name="author_2")
        author_3 = Author.objects.create(username="author_3", display_name="author_3")
        FollowRequest.objects.create(sender=author_2, receiver=author_1)
        FollowRequest.objects.create(sender=author_3, receiver=author_1)
        
        url = f'/api/authors/{author_1.id}/follow-requests/'
        self.client.force_authenticate(user=mock.Mock())
        response = self.client.get(url)

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(2, len(response.data))
        fr1 = response.data[0]
        fr2 = response.data[1]
        expected_fields = ['id', 'url', 'display_name', 'profile_image', 'github_handle']
        for field in expected_fields:
            self.assertTrue(field in fr1)
            self.assertTrue(field in fr2)

        self.assertTrue(fr1['url'].startswith('http'))
        self.assertTrue(fr1['url'].endswith(f'/authors/{author_2.id}/'))
        self.assertEqual(str(author_2.id), fr1['id'])
        self.assertEqual(str(author_3.id), fr2['id'])

    def test_author_has_no_follow_requests(self):
        author_1 = Author.objects.create(username="author_1", display_name="author_1")
        url = f'/api/authors/{author_1.id}/follow-requests/'
        self.client.force_authenticate(user=mock.Mock())
        response = self.client.get(url)

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(0, len(response.data))

    def test_author_does_not_exist(self):
        author_1 = Author.objects.create(username="author_1", display_name="author_1")
        url = f'/api/authors/{uuid.uuid4()}/follow-requests/'
        self.client.force_authenticate(user=mock.Mock())
        response = self.client.get(url)
        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)


class FollowersViewTestCase(APITestCase):
    def test_author_has_multiple_followers(self):
        author_1 = Author.objects.create(username="author_1", display_name="author_1")
        author_2 = Author.objects.create(username="author_2", display_name="author_2")
        author_3 = Author.objects.create(username="author_3", display_name="author_3")
        Follow.objects.create(followee=author_1, follower=author_2)
        Follow.objects.create(followee=author_1, follower=author_3)
        
        url = f'/api/authors/{author_1.id}/followers/'
        self.client.force_authenticate(user=mock.Mock())
        response = self.client.get(url)
        
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(2, len(response.data))
        f1 = response.data[0]
        f2 = response.data[1]
        expected_fields = ['id', 'url', 'display_name', 'profile_image', 'github_handle']
        for field in expected_fields:
            self.assertTrue(field in f1)
            self.assertTrue(field in f2)

        self.assertTrue(f1['url'].startswith('http'))
        self.assertTrue(f1['url'].endswith(f'/authors/{author_2.id}/'))
        self.assertEqual(str(author_2.id), f1['id'])
        self.assertEqual(str(author_3.id), f2['id'])
    
    def test_author_has_no_followers(self):
        author_1 = Author.objects.create(username="author_1", display_name="author_1")
        url = f'/api/authors/{author_1.id}/followers/'
        self.client.force_authenticate(user=mock.Mock())
        response = self.client.get(url)

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(0, len(response.data))
    
    @responses.activate
    def test_author_has_a_combination_of_local_and_remote_followers(self):
        local_author = Author.objects.create(username="local_author", display_name="local_author")
        local_author_2 = Author.objects.create(username="author_2", display_name="author_2")
        node_user = Author.objects.create(username="node_user", display_name="node_user", is_remote_user=True)
        node = Node.objects.create(api_url="https://social-distribution-1.herokuapp.com/api", user=node_user,
                                   auth_username="team14", auth_password="password-team14", team=14)
        remote_author_id = uuid.uuid4()
        remote_author = RemoteAuthor.objects.create(id=remote_author_id, node=node)
        Follow.objects.create(followee=local_author, remote_follower=remote_author)
        Follow.objects.create(followee=local_author, follower=local_author_2)
        
        remote_author_json = {
            "url": f"https://social-distribution-1.herokuapp.com/api/authors/{remote_author_id}",
            "id": f"{remote_author_id}",
            "display_name": "Jake",
            "profile_image": "",
            "github_handle": ""
        }
        responses.add(
            responses.GET,
            f"https://social-distribution-1.herokuapp.com/api/authors/{remote_author_id}",
            json=remote_author_json,
            status=200,
        )
        
        url = f'/api/authors/{local_author.id}/followers/'
        self.client.force_authenticate(user=local_author)
        response = self.client.get(url)

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(2, len(response.data))
        self.assertEqual("Jake", response.data[0]['display_name'])
        self.assertEqual("author_2", response.data[1]['display_name'])

    @responses.activate
    def test_author_has_a_combination_of_local_and_remote_followers_team10(self):
        local_author = Author.objects.create(username="local_author", display_name="local_author")
        local_author_2 = Author.objects.create(username="author_2", display_name="author_2")
        node_user = Author.objects.create(username="node_user", display_name="node_user", is_remote_user=True)
        node = Node.objects.create(api_url="https://social-distribution-1.herokuapp.com/api", user=node_user,
                                   auth_username="team10", auth_password="password-team10", team=10)
        remote_author_id = uuid.uuid4()
        remote_author = RemoteAuthor.objects.create(id=remote_author_id, node=node)
        Follow.objects.create(followee=local_author, remote_follower=remote_author)
        Follow.objects.create(followee=local_author, follower=local_author_2)

        remote_author_json = {
            "type":"author",
            "url": f"https://social-distribution-1.herokuapp.com/api/authors/{remote_author.id}/",
            "id": f"{remote_author.id}",
            "host":"host",
            "displayName": "Jake",
            "profileImage": "",
            "github": ""
        }
        
        responses.add(
            responses.GET,
            f"https://social-distribution-1.herokuapp.com/api/authors/{remote_author_id}",
            json=remote_author_json,
            status=200,
        )
        
        url = f'/api/authors/{local_author.id}/followers/'
        self.client.force_authenticate(user=local_author)
        response = self.client.get(url)

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(2, len(response.data))
        self.assertEqual("Jake", response.data[0]['display_name'])
        self.assertEqual("author_2", response.data[1]['display_name'])

    

    @responses.activate
    def test_author_has_a_combination_of_local_and_remote_followers_team16(self):
        local_author = Author.objects.create(username="local_author", display_name="local_author")
        local_author_2 = Author.objects.create(username="author_2", display_name="author_2")
        node_user = Author.objects.create(username="node_user", display_name="node_user", is_remote_user=True)
        node = Node.objects.create(api_url="https://social-distribution-1.herokuapp.com/api", user=node_user,
                                   auth_username="team16", auth_password="password-team16", team=16)
        remote_author_id = uuid.uuid4()
        remote_author = RemoteAuthor.objects.create(id=remote_author_id, node=node)
        Follow.objects.create(followee=local_author, remote_follower=remote_author)
        Follow.objects.create(followee=local_author, follower=local_author_2)

        remote_author_json = {
            "type":"author",
            "url": f"https://social-distribution-1.herokuapp.com/api/authors/{remote_author.id}/",
            "id": f"https://social-distribution-1.herokuapp.com/api/authors/{remote_author.id}/",
            "host":"host",
            "displayName": "Jake",
            "profileImage": "",
            "github": ""
        }
        
        responses.add(
            responses.GET,
            f"https://social-distribution-1.herokuapp.com/api/authors/{remote_author_id}",
            json=remote_author_json,
            status=200,
        )
        
        url = f'/api/authors/{local_author.id}/followers/'
        self.client.force_authenticate(user=local_author)
        response = self.client.get(url)

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(2, len(response.data))
        self.assertEqual("Jake", response.data[0]['display_name'])
        self.assertEqual("author_2", response.data[1]['display_name'])
class FollowersDetailViewTestCase(APITestCase):
    def test_author_accepts_a_follow_request(self):
        author_1 = Author.objects.create(username="author_1", display_name="author_1")
        author_2 = Author.objects.create(username="author_2", display_name="author_2")
        FollowRequest.objects.create(sender=author_2, receiver=author_1)
        self.assertEqual(1, FollowRequest.objects.count())
        
        # author_1 accepts the request
        url = f'/api/authors/{author_1.id}/followers/{author_2.id}/'
        payload = {
            "follow_request_sender": {
                "url": f'http://127.0.0.1:5054/authors/{author_2.id}',
                "id": author_2.id,
            }
        }
        self.client.force_authenticate(user=author_1)
        response = self.client.put(url, data=payload, format="json")
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        self.assertEqual(1, Follow.objects.count())
        self.assertEqual(0, FollowRequest.objects.count())

        new_follow = Follow.objects.first()
        self.assertEqual(author_1, new_follow.followee)
        self.assertEqual(author_2, new_follow.follower)
        
    def test_follow_request_does_not_exist(self):
        """Author cannot accept a follow request when a request does not exist to begin with"""
        author_1 = Author.objects.create(username="author_1", display_name="author_1")
        author_2 = Author.objects.create(username="author_2", display_name="author_2")
        self.assertEqual(0, FollowRequest.objects.count())

        url = f'/api/authors/{author_1.id}/followers/{author_2.id}/'
        payload = {
            "follow_request_sender": {
                "url": f'http://127.0.0.1:5054/authors/{author_2.id}',
                "id": author_2.id,
            }
        }
        self.client.force_authenticate(user=author_1)
        response = self.client.put(url, data=payload, format="json")
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)
        self.assertEqual(0, Follow.objects.count())
    
    def test_valid_request_data_is_not_given(self):
        author_1 = Author.objects.create(username="author_1", display_name="author_1")
        author_2 = Author.objects.create(username="author_2", display_name="author_2")
        FollowRequest.objects.create(sender=author_2, receiver=author_1)
        self.assertEqual(1, FollowRequest.objects.count())
        
        # author_1 accepts the request
        url = f'/api/authors/{author_1.id}/followers/{author_2.id}/'
        payload = {
            "follow_request_sender": {
                "id": author_2.id,
            }
        }
        self.client.force_authenticate(user=author_1)
        response = self.client.put(url, data=payload, format="json")
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)
        self.assertEqual(0, Follow.objects.count())
    
    def test_author_does_not_exist(self):
        author_1 = Author.objects.create(username="author_1", display_name="author_1")
        non_existent_author_id = str(uuid.uuid4())
        url = f'/api/authors/{author_1.id}/followers/{non_existent_author_id}/'
        payload = {
            "follow_request_sender": {
                "url": f'http://127.0.0.1:5054/authors/{non_existent_author_id}',
                "id": non_existent_author_id,
            }
        }
        self.client.force_authenticate(user=author_1)
        response = self.client.put(url, data=payload, format="json")
        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)
    
    def test_reverse_follow_is_allowed(self):
        author_1 = Author.objects.create(username="author_1", display_name="author_1")
        author_2 = Author.objects.create(username="author_2", display_name="author_2")
        Follow.objects.create(follower=author_2, followee=author_1)
        FollowRequest.objects.create(sender=author_1, receiver=author_2)
        self.assertEqual(1, Follow.objects.count())
        self.assertEqual(1, FollowRequest.objects.count())
        
        # author_2 accepts the request
        url = f'/api/authors/{author_2.id}/followers/{author_1.id}/'
        payload = {
            "follow_request_sender": {
                "url": f'http://127.0.0.1:5054/authors/{author_1.id}',
                "id": author_1.id,
            }
        }
        self.client.force_authenticate(user=author_2)
        response = self.client.put(url, data=payload, format="json")
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        self.assertEqual(2, Follow.objects.count())
        self.assertEqual(0, FollowRequest.objects.count())

    def test_author_accepts_a_remote_follow_request(self):
        local_author = Author.objects.create(username="local_author", display_name="local_author")
        node_user = Author.objects.create(username="node_user", display_name="node_user", is_remote_user=True)
        node = Node.objects.create(api_url="https://social-distribution-1.herokuapp.com/api", user=node_user,
                                   auth_username="team14", auth_password="password-team14", team=14)
        remote_author_id = uuid.uuid4()
        remote_author = RemoteAuthor.objects.create(id=remote_author_id, node=node)
        FollowRequest.objects.create(remote_sender=remote_author, receiver=local_author)
        
        url = f'/api/authors/{local_author.id}/followers/{remote_author_id}/'
        payload = {
            "follow_request_sender": {
                "url": f'https://social-distribution-1.herokuapp.com/apiauthors/{remote_author_id}',
                "id": remote_author_id,
            }
        }
        self.client.force_authenticate(user=local_author)
        response = self.client.put(url, data=payload, format="json")
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        self.assertEqual(1, Follow.objects.count())
        self.assertEqual(0, FollowRequest.objects.count())
        new_follow = Follow.objects.first()
        self.assertEqual(local_author, new_follow.followee)
        self.assertEqual(remote_author, new_follow.remote_follower)
    
    def test_get(self):
        """The given foreign_author_id is a follower of author_id"""
        author_1 = Author.objects.create(username="author_1", display_name="author_1")
        author_2 = Author.objects.create(username="author_2", display_name="author_2")
        Follow.objects.create(follower=author_2, followee=author_1)
        url = f'/api/authors/{author_1.id}/followers/{author_2.id}/'
        self.client.force_authenticate(user=mock.Mock())
        response = self.client.get(url)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
    
    def test_get_remote_follower(self):
        local_author = Author.objects.create(username="local_author", display_name="local_author")
        node_user = Author.objects.create(username="node_user", display_name="node_user", is_remote_user=True)
        node = Node.objects.create(api_url="https://social-distribution-1.herokuapp.com/api", user=node_user,
                                   auth_username="team14", auth_password="password-team14", team=14)
        remote_author = RemoteAuthor.objects.create(id=uuid.uuid4(), node=node)
        Follow.objects.create(remote_follower=remote_author, followee=local_author)
        
        url = f'/api/authors/{local_author.id}/followers/{remote_author.id}/'
        self.client.force_authenticate(user=node_user)
        response = self.client.get(url)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
    
    def test_get_404(self):
        """the given foreign_author_id is NOT a follower of author_id"""
        author_1 = Author.objects.create(username="author_1", display_name="author_1")
        author_2 = Author.objects.create(username="author_2", display_name="author_2")
        url = f'/api/authors/{author_1.id}/followers/{author_2.id}/'
        self.client.force_authenticate(user=mock.Mock())
        response = self.client.get(url)
        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)
    
    def test_delete(self):
        """Remove foreign_author_id as a follower of author_id"""
        author_1 = Author.objects.create(username="author_1", display_name="author_1")
        author_2 = Author.objects.create(username="author_2", display_name="author_2")
        Follow.objects.create(follower=author_2, followee=author_1)
        self.assertEqual(1, Follow.objects.count())

        url = f'/api/authors/{author_1.id}/followers/{author_2.id}/'
        payload = {
            "follower": {
                "url": f'http://127.0.0.1:5054/authors/{author_2.id}',
                "id": author_2.id,
            }
        }
        self.client.force_authenticate(user=author_1)
        response = self.client.delete(url, data=payload, format="json")
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(0, Follow.objects.count())
    
    def test_delete_404(self):
        """Cannot remove a follower that does not exist"""
        author_1 = Author.objects.create(username="author_1", display_name="author_1")
        author_2 = Author.objects.create(username="author_2", display_name="author_2")
        url = f'/api/authors/{author_1.id}/followers/{author_2.id}/'
        payload = {
            "follower": {
                "url": f'http://127.0.0.1:5054/authors/{author_2.id}',
                "id": author_2.id,
            }
        }
        self.client.force_authenticate(user=author_1)
        response = self.client.delete(url, data=payload, format="json")
        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)

class PostTestCase(APITestCase):
    
    def test_get_public_post(self):
        author_1 = Author.objects.create(username="author_1", display_name="author_1")
        current_date_string = datetime.datetime.utcnow().replace(tzinfo=utc)
        
        post_1 = Post.objects.create(
            author =author_1,
            created_at=current_date_string,
            title="Test Post",
            description="Testing post",
            source="source",
            origin="origin",
            unlisted=False,
            content_type= "text/plain",
            content="Some content",
            visibility= "PUBLIC"
        )
        url = f'/api/authors/{author_1.id}/posts/{post_1.id}/'
        self.client.force_authenticate(user=mock.Mock())
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        test_author = response.data["author"]
        self.assertEqual(test_author["id"], str(author_1.id))
        self.assertNotEqual(response.data["created_at"], None)
        self.assertEqual(response.data["title"], "Test Post")
        self.assertEqual(response.data["description"], "Testing post")
        self.assertEqual(response.data["source"], "source")
        self.assertEqual(response.data["origin"], "origin")
        self.assertEqual(response.data["unlisted"], False)
        self.assertEqual(response.data["content_type"], "text/plain")
        self.assertEqual(response.data["content"], "Some content")
        self.assertEqual(response.data["visibility"], "PUBLIC")
    
    @responses.activate
    def test_get_remote_public_post_from_team14(self):
        local_author = Author.objects.create(username="local_author", display_name="local_author")
        node_user = Author.objects.create(username="node_user", display_name="node_user", is_remote_user=True)
        node = Node.objects.create(api_url="https://social-distribution-1.herokuapp.com/api", user=node_user,
                                   auth_username="team14", auth_password="password-team14", team=14)
        remote_author_id = uuid.uuid4()
        remote_post_id = uuid.uuid4()
        
        remote_author_json = {
            "url": f"https://social-distribution-1.herokuapp.com/api/authors/{remote_author_id}",
            "id": f"{remote_author_id}",
            "display_name": "Jake",
            "profile_image": "",
            "github_handle": ""
        }
        responses.add(
            responses.GET,
            f"https://social-distribution-1.herokuapp.com/api/authors/{remote_author_id}",
            json=remote_author_json,
            status=200,
        )
        remote_post_json = {
            "id": f"{remote_post_id}",
            "author": remote_author_json,
            "created_at": "2022-10-22T05:06:49.477100Z",
            "edited_at": "2022-10-22T23:27:41.589319Z",
            "title": "my first post!",
            "description": "Hello world",
            "source": "",
            "origin": "",
            "unlisted": False,
            "content_type": "text/plain",
            "content": "change the content",
            "visibility": "PUBLIC"
        }
        responses.add(
            responses.GET,
            f"https://social-distribution-1.herokuapp.com/api/authors/{remote_author_id}/posts/{remote_post_id}",
            json=remote_post_json,
            status=200,
        )
        
        url = f'/api/authors/{remote_author_id}/posts/{remote_post_id}/'
        self.client.force_authenticate(user=local_author)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(remote_post_json, response.data)
    
    @responses.activate
    def test_get_remote_public_post_from_team10(self):
        local_author = Author.objects.create(username="local_author", display_name="local_author")
        node_user = Author.objects.create(username="node_user", display_name="node_user", is_remote_user=True)
        node = Node.objects.create(api_url="https://social-distribution-1.herokuapp.com/api", user=node_user,
                                   auth_username="team10", auth_password="password-team10", team=10)
        remote_author_id = uuid.uuid4()
        remote_post_id = uuid.uuid4()
        
        remote_author_json = {
            "type": "author",
            "url": f"https://social-distribution-1.herokuapp.com/api/authors/{remote_author_id}",
            "id": f"{remote_author_id}",
            "host": "string",
            "displayName": "Jake",
            "profileImage": "",
            "github": "",    
        }
        responses.add(
            responses.GET,
            f"https://social-distribution-1.herokuapp.com/api/authors/{remote_author_id}",
            json=remote_author_json,
            status=200,
        )

        remote_post_json = {
            "type": "post",
            "title": "my first post!",
            "id": f"{remote_post_id}",
            "source": "",
            "origin": "",
            "description": "Hello world",
            "contentType": "text/markdown",
            "author": remote_author_json,
            "categories": ["string"],
            "count": 0,
            "comments": "string",
            "published": "2019-08-24T14:15:22Z",
            "visibility": "public",
            "unlisted": False,
            "commentSrc": [],
        }
            
        responses.add(
            responses.GET,
            f"https://social-distribution-1.herokuapp.com/api/authors/{remote_author_id}/posts/{remote_post_id}",
            json=remote_post_json,
            status=200,
        )
        
        url = f'/api/authors/{remote_author_id}/posts/{remote_post_id}/'
        self.client.force_authenticate(user=local_author)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        converted_remote_post = {
            "id": f"{remote_post_id}",
            "author": {
                "url": f"https://social-distribution-1.herokuapp.com/api/authors/{remote_author_id}",
                "id": f"{remote_author_id}",
                "display_name": "Jake",
                "profile_image": "",
                "github_handle": "",
            },
            "created_at": "2019-08-24T14:15:22Z",
            "edited_at": None,
            "title": "my first post!",
            "description": "Hello world",
            "visibility": "PUBLIC",
            "source": "",
            "origin":"",
            "unlisted": False,
            "content_type": "text/markdown",
            "content": None,
            "likes_count": 0,
            "count": 0,
            "comments": "string",
            "comments_src": {
                "type": "comments",
                "page": 1,
                "size": 0,
                "comments": []
            }
        }
        self.assertEqual(converted_remote_post, response.data)

    @responses.activate
    def test_get_remote_public_post_from_team16(self):
        local_author = Author.objects.create(username="local_author", display_name="local_author")
        node_user = Author.objects.create(username="node_user", display_name="node_user", is_remote_user=True)
        node = Node.objects.create(api_url="https://social-distribution-1.herokuapp.com/api", user=node_user,
                                   auth_username="team16", auth_password="password-team16", team=16)
        remote_author_id = uuid.uuid4()
        remote_post_id = uuid.uuid4()
        
        remote_author_json = {
            "type": "author",
            "url": f"https://social-distribution-1.herokuapp.com/api/authors/{remote_author_id}",
            "id": f"https://social-distribution-1.herokuapp.com/api/authors/{remote_author_id}",
            "host": "string",
            "displayName": "Jake",
            "profileImage": "",
            "github": "",    
        }
        responses.add(
            responses.GET,
            f"https://social-distribution-1.herokuapp.com/api/authors/{remote_author_id}",
            json=remote_author_json,
            status=200,
        )

        remote_post_json = {
            "type": "post",
            "title": "my first post!",
            "id": f"{remote_post_id}",
            "source": "",
            "origin": "",
            "description": "Hello world",
            "content": "hello",
            "contentType": "text/markdown",
            "author": remote_author_json,
            "count": 0,
            "comments": "string",
            "published": "2019-08-24T14:15:22Z",
            "visibility": "PUBLIC",
            "unlisted": False
        }
            
        responses.add(
            responses.GET,
            f"https://social-distribution-1.herokuapp.com/api/authors/{remote_author_id}/posts/{remote_post_id}",
            json=remote_post_json,
            status=200,
        )
        
        url = f'/api/authors/{remote_author_id}/posts/{remote_post_id}/'
        self.client.force_authenticate(user=local_author)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        converted_remote_post = {
            "id": f"{remote_post_id}",
            "author": {
                "url": f"https://social-distribution-1.herokuapp.com/api/authors/{remote_author_id}",
                "id": f"{remote_author_id}",
                "display_name": "Jake",
                "profile_image": "",
                "github_handle": "",
            },
            "created_at": "2019-08-24T14:15:22Z",
            "edited_at": None,
            "title": "my first post!",
            "description": "Hello world",
            "visibility": "PUBLIC",
            "source": "",
            "origin":"",
            "unlisted": False,
            "content_type": "text/markdown",
            "content": "hello",
            "likes_count": 0
        }
        self.assertEqual(converted_remote_post, response.data)

    def test_cannot_get_private_post(self):
        author_1 = Author.objects.create(username="author_1", display_name="author_1")
        author_2 = Author.objects.create(username="author_2", display_name="author_2")
        current_date_string = datetime.datetime.utcnow().replace(tzinfo=utc)
        
        post_1 = Post.objects.create(
            author =author_1,
            created_at=current_date_string,
            title="Test Post",
            description="Testing post",
            source="source",
            origin="origin",
            unlisted=False,
            content_type= "text/plain",
            content="Some content",
            visibility= "PRIVATE"
        )

        url = f'/api/authors/{author_1.id}/posts/{post_1.id}/'
        self.client.force_authenticate(user=author_2)
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
    def test_cannot_get_friends_post(self):
        author_1 = Author.objects.create(username="author_1", display_name="author_1")
        author_2 = Author.objects.create(username="author_2", display_name="author_2")
        current_date_string = datetime.datetime.utcnow().replace(tzinfo=utc)

        post_1 = Post.objects.create(
            author =author_1,
            created_at=current_date_string,
            title="Test Post",
            description="Testing post",
            source="source",
            origin="origin",
            unlisted=False,
            content_type= "text/plain",
            content="Some content",
            visibility= "FRIENDS"
        )

        url = f'/api/authors/{author_1.id}/posts/{post_1.id}/'
        self.client.force_authenticate(user=author_2)
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)   

    def test_get_404(self):
        author_1 = Author.objects.create(username="author_1", display_name="author_1")
        fake_post_id = uuid.uuid4()
        url = f'/api/authors/{author_1.id}/posts/{fake_post_id}/'
        self.client.force_authenticate(user=mock.Mock())
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_edit_posts(self):
        """POST request works on all editable data fields"""
        author_1 = Author.objects.create() 
        author_1.set_password("pass123")
        author_1.save()
        request_payload = {"username": "author_1", "password": "pass123"}
        # response = self.client.post("/login/", data=request_payload, format="json")
        self.client.force_authenticate(user=author_1)
        current_date_string = datetime.datetime.utcnow().replace(tzinfo=utc)
        post_1 = Post.objects.create(
            author =author_1,
            created_at=current_date_string,
            edited_at=current_date_string,
            title="Test Post",
            description="Testing post",
            source="source",
            origin="origin",
            unlisted=False,
            content_type= "text/plain",
            content="Some content",
            visibility= "PUBLIC"
        )
        url = f'/api/authors/{author_1.id}/posts/{post_1.id}/'
        self.client.force_authenticate(user=author_1)
        payload = {
            "title": "Mark McGoey",
            "description": "new description",
            "unlisted":True,
            "content":"Some new content"
        }
        response = self.client.post(url,data=payload)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(response.data["title"], "Mark McGoey")
        self.assertEqual(response.data["description"], "new description")
        self.assertEqual(response.data["unlisted"], True)
        self.assertEqual(response.data["content"], "Some new content")

    def test_non_editable_fields(self):
        author_1 = Author.objects.create()  
        author_1.set_password("pass123")
        author_1.save()
        request_payload = {"username": "author_1", "password": "pass123"}
        # response = self.client.post("/login/", data=request_payload, format="json")
        self.client.force_authenticate(user=author_1)
        current_date_string = datetime.datetime.utcnow().replace(tzinfo=utc)
        post_1 = Post.objects.create(
            author =author_1,
            created_at=current_date_string,
            edited_at=current_date_string,
            title="Test Post",
            description="Testing post",
            source="source",
            origin="origin",
            unlisted=False,
            content_type= "text/plain",
            content="Some content",
            visibility= "PUBLIC"
        )
        url = f'/api/authors/{author_1.id}/posts/{post_1.id}/'
        self.client.force_authenticate(user=author_1)
        
        
        payload = {
            "source":"new source",
            "origin": "new origin",  
            "visibility":"FRIENDS"  
        }
        
       
        response = self.client.post(url,data=payload)
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)

    def test_delete(self):
        author_1 = Author.objects.create(username="author_1", display_name="author_1")
        author_1.set_password("pass123")
        author_1.save()
        request_payload = {"username": "author_1", "password": "pass123"}
        # self.client.post("/login/", data=request_payload, format="json")
        self.client.force_authenticate(user=author_1)
        current_date_string = datetime.datetime.utcnow().replace(tzinfo=utc)
        post_1 = Post.objects.create(
            author =author_1,
            created_at=current_date_string,
            title="Test Post",
            description="Testing post",
            source="source",
            origin="origin",
            unlisted=False,
            visibility="PUBLIC"
        )
        url = f'/api/authors/{author_1.id}/posts/{post_1.id}/'
        self.client.force_authenticate(user=author_1)
        self.assertEqual(1, Post.objects.count())
        response = self.client.delete(url)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(0, Post.objects.count())
    
    def test_cannot_delete_another_authors_post(self):
        author_1 = Author.objects.create(username="author_1", display_name="author_1")
        author_2 = Author.objects.create(username="author_2", display_name="author_2")
        author_2.set_password("pass123")
        author_2.save()
        request_payload = {"username": "author_2", "password": "pass123"}
        # self.client.post("/login/", data=request_payload, format="json")
        self.client.force_authenticate(user=author_2)
        current_date_string = datetime.datetime.utcnow().replace(tzinfo=utc)
        post_1 = Post.objects.create(
            author =author_1,
            created_at=current_date_string,
            title="Test Post",
            description="Testing post",
            source="source",
            origin="origin",
            unlisted=False
        )
        url = f'/api/authors/{author_1.id}/posts/{post_1.id}/'
        self.client.force_authenticate(user=author_2)
        self.assertEqual(1, Post.objects.count())
        response = self.client.delete(url)
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)
        self.assertEqual(1, Post.objects.count())

    def test_cannot_edit_another_authors_post(self):
        author_1 = Author.objects.create(username="author_1", display_name="author_1")
        author_2 = Author.objects.create(username="author_2", display_name="author_2")
        author_2.set_password("pass123")
        author_2.save()
        request_payload = {"username": "author_2", "password": "pass123"}
        # self.client.post("/login/", data=request_payload, format="json")
        self.client.force_authenticate(user=author_2)
        current_date_string = datetime.datetime.utcnow().replace(tzinfo=utc)
        post_1 = Post.objects.create(
            author =author_1,
            created_at=current_date_string,
            edited_at=current_date_string,
            title="Test Post",
            description="Testing post",
            source="source",
            origin="origin",
            unlisted=False,
            content_type= "text/plain",
            content="Some content",
            visibility= "PUBLIC"
        )
        url = f'/api/authors/{author_1.id}/posts/{post_1.id}/'
        self.client.force_authenticate(user=author_2)
        payload = {
            "title": "Mark McGoey",
            "description": "new description",
            "unlisted":True,
            "content":"Some new content"
        }
        response = self.client.post(url,data=payload)
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)
       
    def test_cannot_edit_private_post(self):
        author_1 = Author.objects.create(username="author_1", display_name="author_1")
        author_1.set_password("pass123")
        author_1.save()
        request_payload = {"username": "author_1", "password": "pass123"}
        # self.client.post("/login/", data=request_payload, format="json")
        self.client.force_authenticate(user=author_1)
        current_date_string = datetime.datetime.utcnow().replace(tzinfo=utc)
        post_1 = Post.objects.create(
            author =author_1,
            created_at=current_date_string,
            title="Test Post",
            description="Testing post",
            source="source",
            origin="origin",
            unlisted=False,
            visibility="PRIVATE"
        )
        url = f'/api/authors/{author_1.id}/posts/{post_1.id}/'
        self.client.force_authenticate(user=author_1)
        payload = {
            "title": "Mark McGoey",
            "description": "new description",
            "unlisted":True,
            "content":"Some new content"
        }
        response = self.client.post(url,data=payload)
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)
        self.assertNotEqual(post_1.title, payload["title"])
        self.assertNotEqual(post_1.description, payload["description"])
        self.assertNotEqual(post_1.unlisted, payload["unlisted"])
        self.assertNotEqual(post_1.content, payload["content"])
    
    def test_cannot_edit_friend_only_post(self):
        author_1 = Author.objects.create(username="author_1", display_name="author_1")
        author_1.set_password("pass123")
        author_1.save()
        request_payload = {"username": "author_1", "password": "pass123"}
        # self.client.post("/login/", data=request_payload, format="json")
        self.client.force_authenticate(user=author_1)
        current_date_string = datetime.datetime.utcnow().replace(tzinfo=utc)
        post_1 = Post.objects.create(
            author =author_1,
            created_at=current_date_string,
            title="Test Post",
            description="Testing post",
            source="source",
            origin="origin",
            unlisted=False,
            visibility="FRIENDS"
        )
        url = f'/api/authors/{author_1.id}/posts/{post_1.id}/'
        self.client.force_authenticate(user=author_1)
        payload = {
            "title": "Mark McGoey",
            "description": "new description",
            "unlisted":True,
            "content":"Some new content"
        }
        response = self.client.post(url,data=payload)
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)
        self.assertNotEqual(post_1.title, payload["title"])
        self.assertNotEqual(post_1.description, payload["description"])
        self.assertNotEqual(post_1.unlisted, payload["unlisted"])
        self.assertNotEqual(post_1.content, payload["content"])

    def test_cannot_delete_friend_only_post(self):
        author_1 = Author.objects.create(username="author_1", display_name="author_1")
        author_1.set_password("pass123")
        author_1.save()
        request_payload = {"username": "author_1", "password": "pass123"}
        # self.client.post("/login/", data=request_payload, format="json")
        self.client.force_authenticate(user=author_1)
        current_date_string = datetime.datetime.utcnow().replace(tzinfo=utc)
        post_1 = Post.objects.create(
            author =author_1,
            created_at=current_date_string,
            title="Test Post",
            description="Testing post",
            source="source",
            origin="origin",
            unlisted=False,
            visibility="FRIENDS"
        )
        url = f'/api/authors/{author_1.id}/posts/{post_1.id}/'
        self.client.force_authenticate(user=author_1)
        self.assertEqual(Post.objects.filter(author=author_1.id).count(),1)
        response = self.client.delete(url)
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)
        self.assertEqual(Post.objects.filter(author=author_1.id).count(),1)

    def test_cannot_delete_private_post(self):
        author_1 = Author.objects.create(username="author_1", display_name="author_1")
        author_1.set_password("pass123")
        author_1.save()
        request_payload = {"username": "author_1", "password": "pass123"}
        # self.client.post("/login/", data=request_payload, format="json")
        self.client.force_authenticate(user=author_1)
        current_date_string = datetime.datetime.utcnow().replace(tzinfo=utc)
        post_1 = Post.objects.create(
            author =author_1,
            created_at=current_date_string,
            title="Test Post",
            description="Testing post",
            source="source",
            origin="origin",
            unlisted=False,
            visibility="PRIVATE"
        )
        url = f'/api/authors/{author_1.id}/posts/{post_1.id}/'
        self.client.force_authenticate(user=author_1)
        self.assertEqual(Post.objects.filter(author=author_1.id).count(),1)
        response = self.client.delete(url)
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)
        self.assertEqual(Post.objects.filter(author=author_1.id).count(),1)
    
    def test_cannot_edit_deleted_post(self):
        author_1 = Author.objects.create(username="author_1", display_name="author_1")
        author_1.set_password("pass123")
        author_1.save()
        request_payload = {"username": "author_1", "password": "pass123"}
        # self.client.post("/login/", data=request_payload, format="json")
        self.client.force_authenticate(user=author_1)
        current_date_string = datetime.datetime.utcnow().replace(tzinfo=utc)
        post_1 = Post.objects.create(
            author =author_1,
            created_at=current_date_string,
            title="Test Post",
            description="Testing post",
            source="source",
            origin="origin",
            unlisted=False,
            visibility="PUBLIC"
        )
        url = f'/api/authors/{author_1.id}/posts/{post_1.id}/'
        self.client.force_authenticate(user=author_1)
        self.assertEqual(Post.objects.filter(author=author_1.id).count(),1)
        response = self.client.delete(url)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(Post.objects.filter(author=author_1.id).count(),0)

        payload = {
            "title": "Mark McGoey",
            "description": "new description",
            "unlisted":True,
            "content":"Some new content"
        }
        response = self.client.post(url,data=payload)
        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)
    
    def test_likes_count(self):
        author_1 = Author.objects.create(username="author_1", display_name="author_1")
        author_2 =  Author.objects.create(username="author_2",display_name="author_2")
        author_3 =  Author.objects.create(username="author_3",display_name="author_3")
        author_4 = Author.objects.create(username="author_4",display_name="author_4")
        
        post_1 = Post.objects.create(
            author =author_1,
            title="Test Post",
            description="Testing post",
            unlisted=False,
            content_type= "text/plain",
            content="Some content",
            visibility= "PUBLIC"
        )
        url = f'/api/authors/{author_1.id}/posts/{post_1.id}/'
        self.client.force_authenticate(user=mock.Mock())
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        likes_count = response.data["likes_count"]
        self.assertEqual(likes_count,0)

        Like.objects.create(author=author_2,post=post_1)
        Like.objects.create(author=author_3,post=post_1)
        Like.objects.create(author=author_4,post=post_1)
        url = f'/api/authors/{author_1.id}/posts/{post_1.id}/'
        self.client.force_authenticate(user=mock.Mock())
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        likes_count = response.data["likes_count"]
        self.assertEqual(likes_count,3)
      

class AllPostTestCase(APITestCase):
    def test_get(self):
        author = Author.objects.create(username="author", display_name="author")
        current_date_string = datetime.datetime.utcnow().replace(tzinfo=utc)
        Post.objects.create(
            author =author,
            created_at=current_date_string,
            title="Test Post ",
            description="Testing post",
            source="source",
            origin="origin",
            unlisted=False,
            visibility = "PUBLIC"
        )
       
        url = f'/api/authors/{author.id}/posts/'
        self.client.force_authenticate(user=mock.Mock())
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        post_1 = response.data[0]
        self.assertEqual(post_1["description"], "Testing post")
    
    def test_get_most_recent_post(self):
        author = Author.objects.create(username="author", display_name="author")
        Post.objects.create(
            author =author,
            title="Test Post 1",
            description="Testing post 1",
            unlisted=False,
            visibility = "PUBLIC"
        )
       
        Post.objects.create(
            author=author,
            title="Test Post 2",
            description="Testing post 2",
            source="source",
            origin="origin",
            unlisted=False
        )

        Post.objects.create(
            author=author,
            title="Test Post 3",
            description="Testing post 3",
            unlisted=False
        )

        Post.objects.create(
            author=author,
            title="Test Post 4",
            description="Testing post 4",
            unlisted=False
        )

        url = f'/api/authors/{author.id}/posts/'
        self.client.force_authenticate(user=mock.Mock())
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # since the posts are ordered in descending order the post that was last created should be first in the list
        post_4 = response.data[0]
        post_3 = response.data[1]
        post_2 = response.data[2]
        post_1 = response.data[3]
        self.assertEqual(post_4["description"], "Testing post 4")
        self.assertEqual(post_3["description"], "Testing post 3")
        self.assertEqual(post_2["description"], "Testing post 2")
        self.assertEqual(post_1["description"], "Testing post 1")
    
    @responses.activate
    def test_get_remote_posts_from_team14_author(self):
        local_author = Author.objects.create(username="local_author", display_name="local_author")
        node_user = Author.objects.create(username="node_user", display_name="node_user", is_remote_user=True)
        node = Node.objects.create(api_url="https://social-distribution-1.herokuapp.com/api", user=node_user,
                                   auth_username="team14", auth_password="password-team14", team=14)
        remote_author_id = uuid.uuid4()
        remote_post_id = uuid.uuid4()
        
        remote_author_json = {
            "url": f"https://social-distribution-1.herokuapp.com/api/authors/{remote_author_id}",
            "id": f"{remote_author_id}",
            "display_name": "Jake",
            "profile_image": "",
            "github_handle": ""
        }
        responses.add(
            responses.GET,
            f"https://social-distribution-1.herokuapp.com/api/authors/{remote_author_id}",
            json=remote_author_json,
            status=200,
        )
        remote_posts_json = [
            {
                "id": f"{remote_post_id}",
                "author": remote_author_json,
                "created_at": "2022-10-22T05:06:49.477100Z",
                "edited_at": "2022-10-22T23:27:41.589319Z",
                "title": "my first post!",
                "description": "Hello world",
                "source": "",
                "origin": "",
                "unlisted": False,
                "content_type": "text/plain",
                "content": "change the content",
                "visibility": "PUBLIC"
            }
        ]
        responses.add(
            responses.GET,
            f"https://social-distribution-1.herokuapp.com/api/authors/{remote_author_id}/posts/",
            json=remote_posts_json,
            status=200,
        )
        
        url = f'/api/authors/{remote_author_id}/posts/'
        self.client.force_authenticate(user=local_author)
        response = self.client.get(url)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(remote_posts_json, response.data)
    
    @responses.activate
    def test_get_remote_posts_from_team10_author(self):
        local_author = Author.objects.create(username="local_author", display_name="local_author")
        node_user = Author.objects.create(username="node_user", display_name="node_user", is_remote_user=True)
        node = Node.objects.create(api_url="https://social-distribution-1.herokuapp.com/api", user=node_user,
                                   auth_username="team10", auth_password="password-team10", team=10)
        remote_author_id = uuid.uuid4()
        remote_post_id = uuid.uuid4()

        remote_author_json = {
            "type":"author",
            "url": f"https://social-distribution-1.herokuapp.com/api/authors/{remote_author_id}",
            "id": f"{remote_author_id}",
            "host": "string",
            "displayName": "Jake",
            "profileImage": "",
            "github": "",
        }
        
        converted_remote_author_json = {
            "url": f"https://social-distribution-1.herokuapp.com/api/authors/{remote_author_id}",
            "id": f"{remote_author_id}",
            "display_name": "Jake",
            "profile_image": "",
            "github_handle": "",
        }
        responses.add(
            responses.GET,
            f"https://social-distribution-1.herokuapp.com/api/authors/{remote_author_id}",
            json=remote_author_json,
            status=200,
        )

        remote_posts_json ={ 
            "type":"string",
            "items":[ 
                {
                    "type": "post",
                    "title": "my first post!",
                    "id": f"{remote_post_id}",
                    "source": "",
                    "origin": "",
                    "description": "Hello world",
                    "contentType": "text/markdown",
                    "author": remote_author_json,
                    "categories": ["string"],
                    "count": 0,
                    "comments": "string",
                    "published": "2019-08-24T14:15:22Z",
                    "visibility": "public",
                    "unlisted": False,
                    "commentSrc": [],
                }
            ]
        }
        responses.add(
            responses.GET,
            f"https://social-distribution-1.herokuapp.com/api/authors/{remote_author_id}/posts/",
            json=remote_posts_json,
            status=200,
        )
        
        converted_remote_posts_json = [
            {   
                "id": f"{remote_post_id}",
                "author": converted_remote_author_json,
                "created_at": "2019-08-24T14:15:22Z",
                "edited_at": None,
                "title": "my first post!",
                "description": "Hello world",
                "source": "",
                "origin": "",
                "unlisted": False,
                "content_type": "text/markdown",
                "content": None,
                "visibility": "PUBLIC",
                "likes_count": 0,
                "count": 0,
                "comments": "string",
                "comments_src": {
                    "type": "comments",
                    "page": 1,
                    "size": 0,
                    "comments": []
                }
            }
        ]
        
        url = f'/api/authors/{remote_author_id}/posts/'
        self.client.force_authenticate(user=local_author)
        response = self.client.get(url)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(converted_remote_posts_json, response.data)

    @responses.activate
    def test_get_remote_posts_from_team16_author(self):
        local_author = Author.objects.create(username="local_author", display_name="local_author")
        node_user = Author.objects.create(username="node_user", display_name="node_user", is_remote_user=True)
        node = Node.objects.create(api_url="https://social-distribution-1.herokuapp.com/api", user=node_user,
                                   auth_username="team16", auth_password="password-team16", team=16)
        remote_author_id = uuid.uuid4()
        remote_post_id = uuid.uuid4()

        remote_author_json = {
            "type":"author",
            "url": f"https://social-distribution-1.herokuapp.com/api/authors/{remote_author_id}",
            "id":  f"https://social-distribution-1.herokuapp.com/api/authors/{remote_author_id}",
            "host": "string",
            "displayName": "Jake",
            "profileImage": "",
            "github": "",
        }
        
        converted_remote_author_json = {
            "url": f"https://social-distribution-1.herokuapp.com/api/authors/{remote_author_id}",
            "id": f"{remote_author_id}",
            "display_name": "Jake",
            "profile_image": "",
            "github_handle": "",
        }
        responses.add(
            responses.GET,
            f"https://social-distribution-1.herokuapp.com/api/authors/{remote_author_id}",
            json=remote_author_json,
            status=200,
        )

        remote_posts_json ={ 
            "type":"string",
            "items":[ 
                {
                    "type": "post",
                    "title": "my first post!",
                    "id": f"{remote_post_id}",
                    "source": "",
                    "origin": "",
                    "description": "Hello world",
                    "contentType": "text/markdown",
                    "content": "hello",
                    "author": remote_author_json,
                    "count": 0,
                    "comments": "string",
                    "published": "2019-08-24T14:15:22Z",
                    "visibility": "PUBLIC",
                    "unlisted": False
                }
            ]
        }
        responses.add(
            responses.GET,
            f"https://social-distribution-1.herokuapp.com/api/authors/{remote_author_id}/posts/",
            json=remote_posts_json,
            status=200,
        )
        
        converted_remote_posts_json = [
            {   
                "id": f"{remote_post_id}",
                "author": converted_remote_author_json,
                "created_at": "2019-08-24T14:15:22Z",
                "edited_at": None,
                "title": "my first post!",
                "description": "Hello world",
                "source": "",
                "origin": "",
                "unlisted": False,
                "content_type": "text/markdown",
                "content": "hello",
                "visibility": "PUBLIC",
                "likes_count": 0
            }
        ]
        
        url = f'/api/authors/{remote_author_id}/posts/'
        self.client.force_authenticate(user=local_author)
        response = self.client.get(url)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(converted_remote_posts_json, response.data)

    @responses.activate
    def test_get_paginated_remote_posts_from_team14_author(self):
        local_author = Author.objects.create(username="local_author", display_name="local_author")
        node_user = Author.objects.create(username="node_user", display_name="node_user", is_remote_user=True)
        node = Node.objects.create(api_url="https://social-distribution-1.herokuapp.com/api", user=node_user,
                                   auth_username="team14", auth_password="password-team14", team=14)
        remote_author_id = uuid.uuid4()
        remote_post_id = uuid.uuid4()
        
        remote_author_json = {
            "url": f"https://social-distribution-1.herokuapp.com/api/authors/{remote_author_id}",
            "id": f"{remote_author_id}",
            "display_name": "Jake",
            "profile_image": "",
            "github_handle": ""
        }
        responses.add(
            responses.GET,
            f"https://social-distribution-1.herokuapp.com/api/authors/{remote_author_id}",
            json=remote_author_json,
            status=200,
        )
        remote_posts_json = {
            "count": 1,
            "next": None,
            "previous": None,
            "results": [
                {
                    "id": f"{remote_post_id}",
                    "author": remote_author_json,
                    "created_at": "2022-10-22T05:06:49.477100Z",
                    "edited_at": "2022-10-22T23:27:41.589319Z",
                    "title": "my first post!",
                    "description": "Hello world",
                    "source": "",
                    "origin": "",
                    "unlisted": False,
                    "content_type": "text/plain",
                    "content": "change the content",
                    "visibility": "PUBLIC"
                }
            ]
        }
        responses.add(
            responses.GET,
            f"https://social-distribution-1.herokuapp.com/api/authors/{remote_author_id}/posts/?page=1&size=10",
            json=remote_posts_json,
            status=200,
        )
        
        url = f"/api/authors/{remote_author_id}/posts/?page=1&size=10"
        self.client.force_authenticate(user=local_author)
        response = self.client.get(url)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(remote_posts_json, response.data)
        
 
    def test_send_friend_post_to_inbox(self):
        author_1 = Author.objects.create(username="author_1", display_name="author_1")
        author_1.set_password("pass123")
        author_1.save()
        request_payload = {"username": "author_1", "password": "pass123"}
        # self.client.post("/login/", data=request_payload, format="json")
        self.client.force_authenticate(user=author_1)
        author_2 = Author.objects.create(username="author_2", display_name="author_2")
        author_3 = Author.objects.create(username="author_3", display_name="author_3")
        author_4 = Author.objects.create(username="author_4", display_name="author_4")
        author_5 = Author.objects.create(username="author_5", display_name="author_5")
        # creating two extra authors but not adding them as followers to ensure that a friend post is only sent to friends
        Author.objects.create(username="author_6", display_name="author_6")
        Author.objects.create(username="author_7", display_name="author_7")   
        Follow.objects.create(follower=author_2,followee=author_1)
        Follow.objects.create(follower=author_3,followee=author_1)
        Follow.objects.create(follower=author_4,followee=author_1)
        Follow.objects.create(follower=author_5,followee=author_1)
        payload = {
            "title": "Mark McGoey",
            "description": "new description",
            "unlisted":False,
            "content":"Some new content",
            "visibility":"FRIENDS",
            "content_type":"text/plain"
        }
        url = f'/api/authors/{author_1.id}/posts/'
        self.client.force_authenticate(user=author_1)
        response = self.client.post(url,data=payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        inbox = Inbox.objects.all()
        self.assertEqual(4,Inbox.objects.count())
        self.assertEqual(author_2, inbox[0].target_author)
        self.assertEqual(author_3, inbox[1].target_author)
        self.assertEqual(author_4, inbox[2].target_author)
        self.assertEqual(author_5, inbox[3].target_author)

    def test_send_private_post_to_inbox(self):
        author_1 = Author.objects.create(username="author_1", display_name="author_1")
        author_1.set_password("pass123")
        author_1.save()
        request_payload = {"username": "author_1", "password": "pass123"}
        # self.client.post("/login/", data=request_payload, format="json")
        self.client.force_authenticate(user=author_1)
        author_2 = Author.objects.create(username="author_2", display_name="author_2")
        payload = {
            "title": "Mark McGoey",
            "description": "new description",
            "unlisted":True,
            "content":"Some new content",
            "visibility":"PRIVATE",
            "content_type":"text/plain",
            "receiver": {
            "url": f'http://127.0.0.1:5054/authors/{author_2.id}/',
            "id": author_2.id,
            }
        }
        
        url = f'/api/authors/{author_1.id}/posts/'
        self.client.force_authenticate(user=author_1)
        response = self.client.post(url,data=payload,format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        inbox = Inbox.objects.all()
        self.assertEqual(1,Inbox.objects.count())
        self.assertEqual(author_2, inbox[0].target_author)
        self.assertEqual(payload["title"],inbox[0].post.title)
        self.assertEqual(payload["description"],inbox[0].post.description)
        self.assertEqual(payload["unlisted"],inbox[0].post.unlisted)
        self.assertEqual(payload["visibility"],inbox[0].post.visibility)
        self.assertEqual(payload["content_type"],inbox[0].post.content_type)

    def test_cannot_create_new_posts_for_other_authors(self):
        author_1 = Author.objects.create(username="author_1", display_name="author_1")
        author_2 = Author.objects.create(username="author_2", display_name="author_2")
        author_2.set_password("pass123")
        author_2.save()
        request_payload = {"username": "author_2", "password": "pass123"}
        # self.client.post("/login/", data=request_payload, format="json") 
        self.client.force_authenticate(user=author_2)
        payload = {
            "title": "Mark McGoey",
            "description": "new description",
            "unlisted":True,
            "content":"Some new content",
            "visibility":"FRIENDS",
            "content_type":"text/plain"
        }
        url = f'/api/authors/{author_1.id}/posts/'
        self.client.force_authenticate(user=author_2)
        response = self.client.post(url,data=payload,format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_create_post_missing_fields(self):
        author_1 = Author.objects.create(username="author_1", display_name="author_1")
        author_1.set_password("pass123")
        author_1.save()
        request_payload = {"username": "author_1", "password": "pass123"}
        # self.client.post("/login/", data=request_payload, format="json") 
        self.client.force_authenticate(user=author_1)
       

        payload = {
            "unlisted":True,
            "content":"Some new content",
            "visibility":"PUBLIC",     
        }
        
        url = f'/api/authors/{author_1.id}/posts/'
        self.client.force_authenticate(user=author_1)
        response = self.client.post(url, data=payload, format="json")
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)
    
    def test_request_not_valid_when_receiver_not_given(self):
        """Proper serializer fields need to be given"""
        author_1 = Author.objects.create(username="author_1", display_name="author_1")
        author_1.set_password("pass123")
        author_1.save()
        request_payload = {"username": "author_1", "password": "pass123"}
        # self.client.post("/login/", data=request_payload, format="json") 
        self.client.force_authenticate(user=author_1)
       

        payload = {
            "title": "Mark McGoey",
            "description": "new description",
            "unlisted":True,
            "content":"Some new content",
            "visibility":"PRIVATE",
            "content_type":"text/plain",
            
        }
        
        url = f'/api/authors/{author_1.id}/posts/'
        self.client.force_authenticate(user=author_1)
        response = self.client.post(url, data=payload, format="json")
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)
           
    def test_receiver_does_not_exist(self):
        author_1 = Author.objects.create(username="author_1", display_name="author_1")
        author_1.set_password("pass123")
        author_1.save()
        request_payload = {"username": "author_1", "password": "pass123"}
        # self.client.post("/login/", data=request_payload, format="json")
        self.client.force_authenticate(user=author_1)
        
        payload = {
            "title": "Mark McGoey",
            "description": "new description",
            "unlisted":True,
            "content":"Some new content",
            "visibility":"PRIVATE",
            "content_type":"text/plain",
            "receiver": {
            "url": f'http://127.0.0.1:5054/authors/{5080980980}/',
            "id": 5080980980,
            }
        }

        url = f'/api/authors/{author_1.id}/posts/'
        self.client.force_authenticate(user=author_1)
        response = self.client.post(url, data=payload, format="json")
        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)

    def test_get_author_has_no_posts(self):
        author_1 = Author.objects.create(username="author_1", display_name="author_1")
        url = f'/api/authors/{author_1.id}/posts/'
        self.client.force_authenticate(user=mock.Mock())
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_public_post_sent_to_everyones_inbox(self):
        author_1 = Author.objects.create(username="author_1", display_name="author_1")
        author_2 = Author.objects.create(username="author_2", display_name="author_2")
        author_3 = Author.objects.create(username="author_3", display_name="author_3")
        author_4 = Author.objects.create(username="author_4", display_name="author_4")
        author_1.set_password("pass123")
        author_1.save()
        request_payload = {"username": "author_1", "password": "pass123"}
        # self.client.post("/login/", data=request_payload, format="json") 
        self.client.force_authenticate(user=author_1)
        payload = {
            "title": "Mark McGoey",
            "description": "new description",
            "unlisted":False,
            "content":"Some new content",
            "visibility":"PUBLIC",
            "content_type":"text/plain"
        }
        url = f'/api/authors/{author_1.id}/posts/'
        self.client.force_authenticate(user=author_1)
        response = self.client.post(url,data=payload,format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        inbox = Inbox.objects.all()
        self.assertEqual(3, Inbox.objects.count())
        self.assertEqual(author_2, inbox[0].target_author)
        self.assertEqual(author_3, inbox[1].target_author)
        self.assertEqual(author_4, inbox[2].target_author)     

    def test_public_post_sent_to_friends_inbox(self):
        author_1 = Author.objects.create(username="author_1", display_name="author_1")
        author_1.set_password("pass123")
        author_1.save()
        request_payload = {"username": "author_1", "password": "pass123"}
        # self.client.post("/login/", data=request_payload, format="json")
        self.client.force_authenticate(user=author_1)
        author_2 = Author.objects.create(username="author_2", display_name="author_2")
        author_3 = Author.objects.create(username="author_3", display_name="author_3")
        author_4 = Author.objects.create(username="author_4", display_name="author_4")
        author_5 = Author.objects.create(username="author_5", display_name="author_5")
        # there's only 2 followers so the public post should be sent to these two followers plus the non-followers
        Follow.objects.create(follower=author_2,followee=author_1)
        Follow.objects.create(follower=author_3,followee=author_1)
        payload = {
            "title": "Mark McGoey",
            "description": "new description",
            "unlisted":False,
            "content":"Some new content",
            "visibility":"PUBLIC",
            "content_type":"text/plain"
        }
        url = f'/api/authors/{author_1.id}/posts/'
        self.client.force_authenticate(user=author_1)
        response = self.client.post(url,data=payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        inbox = Inbox.objects.all()
        self.assertEqual(4, Inbox.objects.count())
        self.assertEqual(author_2, inbox[0].target_author)
        self.assertEqual(author_3, inbox[1].target_author)
        self.assertEqual(author_4, inbox[2].target_author)
        self.assertEqual(author_5, inbox[3].target_author)

    def test_send_private_post_to_remote_receiver_on_team14_node(self):
        local_author = Author.objects.create(username="local_author", display_name="local_author")
        node_user = Author.objects.create(username="node_user", display_name="node_user", is_remote_user=True)
        node = Node.objects.create(api_url="https://social-distribution-1.herokuapp.com/api", user=node_user,
                                   auth_username="team14", auth_password="password-team14", team=14)
        remote_author_id = uuid.uuid4()
        
        payload = {
            "title": "Super secret post",
            "description": "new description",
            "unlisted":True,
            "content":"Some new content",
            "visibility":"PRIVATE",
            "content_type":"text/plain",
            "receiver": {
                "url": f"https://social-distribution-1.herokuapp.com/api/authors/{remote_author_id}/",
                "id": f"{remote_author_id}",
            }
        }
        url = f'/api/authors/{local_author.id}/posts/'
        self.client.force_authenticate(user=local_author)
        with patch.object(Post, 'update_author_inbox_over_http', return_value=Mock()) as mock_update_inbox_over_http:
            response = self.client.post(url, data=payload, format="json")
        mock_update_inbox_over_http.assert_called_once_with(
            f"https://social-distribution-1.herokuapp.com/api/authors/{remote_author_id}/inbox/",
            node,
            payload["receiver"]
        )
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        self.assertEqual(0, Inbox.objects.count())
        self.assertEqual(1, Post.objects.count())


class InboxViewTestCase(APITestCase):
    def test_get_different_types_of_inbox_items(self):
        author_1 = Author.objects.create(username="author_1", display_name="author_1")
        author_2 = Author.objects.create(username="author_2", display_name="author_2")

        Follow.objects.create(follower=author_1, followee=author_2)
        fr = FollowRequest.objects.create(sender=author_2, receiver=author_1)
        
        post = Post.objects.create(
            author=author_2,
            title="Post 1",
            description="Sample description",
            visibility="FRIENDS",
            content_type="text/plain",
            content="What's up people?"
        )

        # author_1 should see the new post from author_2 and the follow request from author_2
        Inbox.objects.create(target_author=author_1, post=post)
        Inbox.objects.create(target_author=author_1, follow_request_received=fr)
        
        url = f'/api/authors/{author_1.id}/inbox/'
        self.client.force_authenticate(user=author_1)
        response = self.client.get(url)
        
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(2, len(response.data))
        
        follow_inbox = response.data[0]
        post_inbox = response.data[1]
        self.assertEqual("post", post_inbox["type"])
        self.assertEqual("follow", follow_inbox["type"])
        
        # check the data fields of the response
        self.assertEqual("Post 1", post_inbox["title"])
        self.assertEqual("Sample description", post_inbox["description"])
        self.assertTrue("sender" in follow_inbox)
        self.assertTrue("url" in follow_inbox["sender"])
        self.assertTrue(f'http://testserver/api/authors/{author_2.id}/', follow_inbox["sender"]["url"])

    @responses.activate
    def test_get_follow_request_received_from_a_team14_remote_sender(self):
        local_author = Author.objects.create(username="local_author", display_name="local_author")
        node_user = Author.objects.create(username="node_user", display_name="node_user", is_remote_user=True)
        node = Node.objects.create(api_url="https://social-distribution-1.herokuapp.com/api", user=node_user,
                                   auth_username="team14", auth_password="password-team14", team=14)
        remote_author_id = uuid.uuid4()
        remote_author = RemoteAuthor.objects.create(id=remote_author_id, node=node)
        fr = FollowRequest.objects.create(remote_sender=remote_author, receiver=local_author)
        Inbox.objects.create(target_author=local_author, follow_request_received=fr)
        
        remote_author_json = {
            "url": f"https://social-distribution-1.herokuapp.com/api/authors/{remote_author_id}",
            "id": f"{remote_author_id}",
            "display_name": "Jake",
            "profile_image": "",
            "github_handle": ""
        }
        responses.add(
            responses.GET,
            f"https://social-distribution-1.herokuapp.com/api/authors/{remote_author_id}",
            json=remote_author_json,
            status=200,
        )
        
        url = f'/api/authors/{local_author.id}/inbox/'
        self.client.force_authenticate(user=local_author)
        response = self.client.get(url)
        
        expected_output = [
            {
                "type": "follow",
                "sender": remote_author_json
            }
        ]
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(expected_output, response.data)
    
    @responses.activate
    def test_get_follow_request_received_from_a_team10_remote_sender(self):
        local_author = Author.objects.create(username="local_author", display_name="local_author")
        node_user = Author.objects.create(username="node_user", display_name="node_user", is_remote_user=True)
        node = Node.objects.create(api_url="https://social-distribution-1.herokuapp.com/api", user=node_user,
                                   auth_username="team10", auth_password="password-team10", team=10)
        remote_author_id = uuid.uuid4()
        remote_author = RemoteAuthor.objects.create(id=remote_author_id, node=node)
        fr = FollowRequest.objects.create(remote_sender=remote_author, receiver=local_author)
        Inbox.objects.create(target_author=local_author, follow_request_received=fr)
        
        remote_author_json = {
            "type":"author",
            "url": f"https://social-distribution-1.herokuapp.com/api/authors/{remote_author_id}",
            "id": f"{remote_author_id}",
            "host":"string",
            "displayName": "Jake",
            "profileImage": "",
            "github": ""
        }
        converted_remote_author_json = {
           "url": f"https://social-distribution-1.herokuapp.com/api/authors/{remote_author_id}",
            "id": f"{remote_author_id}",
            "display_name": "Jake",
            "profile_image": "",
            "github_handle": "" 
        }
        
        responses.add(
            responses.GET,
            f"https://social-distribution-1.herokuapp.com/api/authors/{remote_author_id}",
            json=remote_author_json,
            status=200,
        )
        
        url = f'/api/authors/{local_author.id}/inbox/'
        self.client.force_authenticate(user=local_author)
        response = self.client.get(url)
        
        expected_output = [
            {
                "type": "follow",
                "sender": converted_remote_author_json
            }
        ]
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(expected_output, response.data)

    @responses.activate
    def test_get_follow_request_received_from_a_team16_remote_sender(self):
        local_author = Author.objects.create(username="local_author", display_name="local_author")
        node_user = Author.objects.create(username="node_user", display_name="node_user", is_remote_user=True)
        node = Node.objects.create(api_url="https://social-distribution-1.herokuapp.com/api", user=node_user,
                                   auth_username="team16", auth_password="password-team16", team=16)
        remote_author_id = uuid.uuid4()
        remote_author = RemoteAuthor.objects.create(id=remote_author_id, node=node)
        fr = FollowRequest.objects.create(remote_sender=remote_author, receiver=local_author)
        Inbox.objects.create(target_author=local_author, follow_request_received=fr)
        
        remote_author_json = {
            "type":"author",
            "url": f"https://social-distribution-1.herokuapp.com/api/authors/{remote_author_id}",
            "id": f"https://social-distribution-1.herokuapp.com/api/authors/{remote_author_id}",
            "host":"string",
            "displayName": "Jake",
            "profileImage": "",
            "github": ""
        }
        converted_remote_author_json = {
           "url": f"https://social-distribution-1.herokuapp.com/api/authors/{remote_author_id}",
            "id": f"{remote_author_id}",
            "display_name": "Jake",
            "profile_image": "",
            "github_handle": "" 
        }
        
        responses.add(
            responses.GET,
            f"https://social-distribution-1.herokuapp.com/api/authors/{remote_author_id}",
            json=remote_author_json,
            status=200,
        )
        
        url = f'/api/authors/{local_author.id}/inbox/'
        self.client.force_authenticate(user=local_author)
        response = self.client.get(url)
        
        expected_output = [
            {
                "type": "follow",
                "sender": converted_remote_author_json
            }
        ]
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(expected_output, response.data)

    @responses.activate
    def test_get_remote_post_from_team14(self):
        local_author = Author.objects.create(username="local_author", display_name="local_author")
        node_user = Author.objects.create(username="node_user", display_name="node_user", is_remote_user=True)
        node = Node.objects.create(api_url="https://social-distribution-1.herokuapp.com/api", user=node_user,
                                   auth_username="team14", auth_password="password-team14", team=14)
        remote_author = RemoteAuthor.objects.create(id=uuid.uuid4(), node=node)
        remote_post = RemotePost.objects.create(id=uuid.uuid4(), author=remote_author)
        Inbox.objects.create(target_author=local_author, remote_post=remote_post)

        remote_posts_json = [
            {
                "id": f"{remote_post.id}",
                "author": {
                    "url": f"https://social-distribution-1.herokuapp.com/api/authors/{remote_author.id}/",
                    "id": f"{remote_author.id}",
                    "display_name": "myuser",
                    "profile_image": "",
                    "github_handle": ""
                },
                "created_at": "2022-10-22T05:06:49.477100Z",
                "edited_at": "2022-10-22T23:27:41.589319Z",
                "title": "my first post!",
                "description": "Hello world",
                "source": "",
                "origin": "",
                "unlisted": False,
                "content_type": "text/plain",
                "content": "change the content",
                "visibility": "FRIENDS"
            }
        ]
        responses.add(
            responses.GET,
            f"https://social-distribution-1.herokuapp.com/api/authors/{remote_author.id}/posts",
            json=remote_posts_json,
            status=200,
        )

        url = f'/api/authors/{local_author.id}/inbox/'
        self.client.force_authenticate(user=local_author)
        response = self.client.get(url)

        expected_output = remote_posts_json[0]
        expected_output["type"] = "post"
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual([expected_output], response.data)

    def test_post_inbox_from_remote_author(self):
        local_author = Author.objects.create(username="local_author", display_name="local_author")
        node_user = Author.objects.create(username="node_user", display_name="node_user", is_remote_user=True)
        node = Node.objects.create(api_url="https://social-distribution-1.herokuapp.com/api", user=node_user,
                                   auth_username="team14", auth_password="password-team14", team=14)
        self.assertEqual(0, RemoteAuthor.objects.count())
        self.assertEqual(0, RemotePost.objects.count())
        self.assertEqual(0, Inbox.objects.count())
        
        remote_post_id = uuid.uuid4()
        remote_author_id = uuid.uuid4()
        payload = {
            "type": "post",
            "post": {
                "id": f"{remote_post_id}",
                "extra_field": "does not matter",
                "author": {
                    "id": f"{remote_author_id}",
                    "url": f"https://social-distribution-1.herokuapp.com/api/authors/{remote_author_id}",
                }
            }
        }
        url = f'/api/authors/{local_author.id}/inbox/'
        self.client.force_authenticate(user=node_user)
        response = self.client.post(url, payload, format='json')
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        self.assertEqual(1, RemoteAuthor.objects.count())
        self.assertEqual(1, RemotePost.objects.count())
        self.assertEqual(1, Inbox.objects.count())
        post = RemotePost.objects.first()
        self.assertEqual(remote_post_id, post.id)
        inbox = Inbox.objects.first()
        self.assertEqual(local_author, inbox.target_author)
        self.assertEqual(post, inbox.remote_post)
        
        # can also handle redundant post inbox requests
        response = self.client.post(url, payload, format='json')
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        self.assertEqual(1, RemoteAuthor.objects.count())
        self.assertEqual(1, RemotePost.objects.count())
        self.assertEqual(1, Inbox.objects.count())


class AllPublicPostsTestCase(APITestCase):
    def test_get_all_public_posts(self):
        author = Author.objects.create(username="author_1", display_name="author_1")
        post_1 = Post.objects.create(
            author=author,
            title="Post 1",
            description="Sample description",
            visibility="FRIENDS",
            content_type="text/plain",
            content="What's up people?"
        )
        post_2 = Post.objects.create(
            author=author,
            title="Post 2",
            description="Sample description 2",
            visibility="PUBLIC",
            content_type="text/plain",
            content="Public service announcement"
        )
        self.assertEqual(2, Post.objects.count())
        
        url = f'/api/posts/'
        self.client.force_authenticate(user=mock.Mock())
        response = self.client.get(url)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(1, len(response.data))
        self.assertEqual("Post 2", response.data[0]["title"])

    @responses.activate
    def test_get_retrives_public_posts_from_remote_nodes(self):
        local_author = Author.objects.create(username="local_author", display_name="local_author")
        node_user = Author.objects.create(username="node_user", display_name="node_user", is_remote_user=True)
        Node.objects.create(api_url="https://social-distribution-1.herokuapp.com/api", user=node_user,
                            auth_username="team14", auth_password="password-team14", team=14)
        node_user_2 = Author.objects.create(username="node_user_2", display_name="node_user_2", is_remote_user=True)
        Node.objects.create(api_url="https://social-distribution-2.herokuapp.com/api", user=node_user_2,
                            auth_username="team14", auth_password="password-team14", team=14)
        remote_author_id_1 = uuid.uuid4()
        remote_author_id_2 = uuid.uuid4()
        
        post = Post.objects.create(
            author=local_author,
            title="Test Post",
            description="Testing post",
            source="source",
            origin="origin",
            unlisted=False,
            visibility = "PUBLIC"
        )
        remote_post_1_json = {
            "author": {
                "id": f"{remote_author_id_1}",
                "url": f"https://social-distribution-1.herokuapp.com/api/authors/{remote_author_id_1}/",
                "display_name": "myuser",
                "profile_image": "",
                "github_handle": ""
            },
            "created_at": "2022-10-22T05:06:49.477100Z",
            "edited_at": "2022-10-22T23:27:41.589319Z",
            "title": "My first post!",
            "description": "Hello world",
            "source": "",
            "origin": "",
            "unlisted": False,
            "content_type": "text/plain",
            "content": "change the content",
            "visibility": "PUBLIC",
        }
        remote_post_2_json = {
            "author": {
                "id": f"{remote_author_id_2}",
                "url": f"https://social-distribution-2.herokuapp.com/api/authors/{remote_author_id_2}/",
                "display_name": "myuser2",
                "profile_image": "",
                "github_handle": ""
            },
            "created_at": "2022-10-22T05:06:49.477100Z",
            "edited_at": "2022-10-22T23:27:41.589319Z",
            "title": "my second post!",
            "description": "Goodnight world",
            "source": "",
            "origin": "",
            "unlisted": False,
            "content_type": "text/plain",
            "content": "change the content",
            "visibility": "PUBLIC",
        }
        responses.add(
            responses.GET,
            f"https://social-distribution-1.herokuapp.com/api/posts/",
            json=[remote_post_1_json],
            status=200,
        )
        responses.add(
            responses.GET,
            f"https://social-distribution-2.herokuapp.com/api/posts/",
            json=[remote_post_2_json],
            status=200,
        )
        
        self.client.force_authenticate(user=local_author)
        url = f'/api/posts/'
        response = self.client.get(url)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(3, len(response.data))
        expected_titles = ["Test Post", "My first post!", "my second post!"]
        self.assertEqual(expected_titles.sort(), [post["title"] for post in response.data].sort())


class DeclineFollowRequestTestCase(APITestCase):
    def test_successful_decline(self):
        author_1 = Author.objects.create(username="author_1", display_name="author_1")
        author_2 = Author.objects.create(username="author_2", display_name="author_2")
        FollowRequest.objects.create(sender=author_2, receiver=author_1)
        self.assertEqual(1, FollowRequest.objects.count())
        
        url = f'/api/authors/{author_1.id}/follow-requests/{author_2.id}/'
        payload = {
            "follow_request_sender": {
                "url": f'http://127.0.0.1:5054/authors/{author_2.id}',
                "id": author_2.id,
            }
        }
        self.client.force_authenticate(user=author_1)
        response = self.client.delete(url, data=payload, format="json")
        
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(0, FollowRequest.objects.count())
    
    def test_follow_request_not_found(self):
        author_1 = Author.objects.create(username="author_1", display_name="author_1")
        author_2 = Author.objects.create(username="author_2", display_name="author_2")
        
        url = f'/api/authors/{author_1.id}/follow-requests/{author_2.id}/'
        payload = {
            "follow_request_sender": {
                "url": f'http://127.0.0.1:5054/authors/{author_2.id}',
                "id": author_2.id,
            }
        }
        self.client.force_authenticate(user=author_1)
        response = self.client.delete(url, data=payload, format="json")
        
        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)


class NodesViewTestCase(APITestCase):
    def test_add_node(self):
        admin = Author.objects.create(username="admin", display_name="admin", is_admin=True)
        self.assertEqual(1, Author.objects.count())
        self.assertEqual(0, Node.objects.count())
        url = '/api/nodes/'
        payload = {
            "api_url":  "https://social-distribution.herokuapp.com/api",
            "node_name": "social-distribution",
            "password": "secure-password",
            "password2": "secure-password",
            "auth_username": "team14",
            "auth_password": "password-team14",
            "team": 14,
        }
        self.client.force_authenticate(user=admin)
        response = self.client.force_authenticate(user=admin)
        response = self.client.post(url, data=payload, format="json")
        
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        self.assertEqual(2, Author.objects.count())
        self.assertEqual(1, Node.objects.count())
        remote_user = Author.objects.order_by("created_at").last()
        node = Node.objects.first()
        self.assertEqual(True, remote_user.is_remote_user)
        self.assertEqual("social-distribution", remote_user.username)
        self.assertEqual("https://social-distribution.herokuapp.com/api", node.api_url)
    
    def test_only_admins_can_add_nodes(self):
        non_admin = Author.objects.create(username="author_1", display_name="author_1")
        url = '/api/nodes/'
        payload = {
            "api_url":  "https://social-distribution.herokuapp.com/api",
            "password": "secure-password",
            "password2": "secure-password",
        }
        self.client.force_authenticate(user=non_admin)
        response = self.client.post(url, data=payload, format="json")
        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)

    @unittest.skip
    def test_get_nodes(self):
        admin = Author.objects.create(username="admin", display_name="admin", is_admin=True)
        node_user_1 = Author.objects.create(username="node_user_1", display_name="node_user_1", 
                                            password="password1", is_remote_user=True)
        Node.objects.create(api_url="https://social-distribution-1.herokuapp.com/api", user=node_user_1,
                            auth_username="team14", auth_password="password-team14")
        node_user_2 = Author.objects.create(username="node_user_2", display_name="node_user_2", 
                                            password="password2", is_remote_user=True)
        Node.objects.create(api_url="https://social-distribution-2.herokuapp.com/api", user=node_user_2,
                            auth_username="team14-2", auth_password="password-team14-2")
        
        url = '/api/nodes/'
        self.client.force_authenticate(user=admin)
        response = self.client.get(url)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        
        expected_output = [
            {
                "id": str(node_user_1.id),
                "password": "password1",
                "node": {
                    "api_url": "https://social-distribution-1.herokuapp.com/api",
                    "team": 14,
                    "auth_username": "team14",
                    "auth_password": "password-team14",
                }
            },
            {
                "id": str(node_user_2.id),
                "password": "password2",
                "node": {
                    "api_url": "https://social-distribution-2.herokuapp.com/api",
                    "team": 14,
                    "auth_username": "team14-2",
                    "auth_password": "password-team14-2",
                }
            }
        ]
        expected_output = sorted(expected_output, key=lambda d: d["id"])
        self.assertEqual(expected_output, response.data)

class NodeModificationTestCase(APITestCase):
    def test_remove_node(self):
        admin = Author.objects.create(username="admin", display_name="admin", is_admin=True)
        node_user_1 = Author.objects.create(username="node_user_1", display_name="node_user_1", 
                                            password="password1", is_remote_user=True)
        Node.objects.create(api_url="https://social-distribution-1.herokuapp.com/api", user=node_user_1)
        self.assertEqual(1, Node.objects.count())
        
        url = f'/api/nodes/{node_user_1.id}/'
        self.client.force_authenticate(user=admin)
        response = self.client.delete(url)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(0, Node.objects.count())

class CustomPermissionsTestCase(APITestCase):
    def setUp(self):
        self.remote_node = Author.objects.create(username="nodeA", display_name="nodeA", is_remote_user=True)
        self.regular_author = Author.objects.create(username="regular_author", display_name="regular_author")

    def test_allows_remote_get_requests(self):
        """IsRemoteGetOnly allows remote GET requests"""
        url = f'/api/authors/{self.regular_author.id}/'
        self.client.force_authenticate(user=self.remote_node)
        response = self.client.get(url)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
    
    def test_does_not_allow_remote_non_get_requests(self):
        """IsRemoteGetOnly does not allow remote non-GET requests"""
        url = f'/api/authors/{self.regular_author.id}/'
        payload = {
            "display_name": "New display name",
            "profile_image": "No image",
            "github_handle": "mmcgoey"
        }
        self.client.force_authenticate(user=self.remote_node)
        response = self.client.post(url, data=payload)
        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)
    
    def test_IsRemoteGetOnly_allows_all_local_requests(self):
        url = f'/api/authors/{self.regular_author.id}/'
        payload = {
            "display_name": "New display name",
            "profile_image": "No image",
            "github_handle": "mmcgoey"
        }
        self.client.force_authenticate(user=self.regular_author)
        response = self.client.post(url, data=payload)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
    
    def test_IsRemotePostOnly_allows_remote_post_requests(self):
        author_1 = Author.objects.create(username="author_1", display_name="author_1")
        author_2 = Author.objects.create(username="author_2", display_name="author_2")
        payload = {
            "type": "follow",
            "sender": {
                "url": f'http://127.0.0.1:5054/authors/{author_1.id}/',
                "id": author_1.id,
            },
            "receiver": {
                "url": f'http://127.0.0.1:5054/authors/{author_2.id}/',
                "id": author_2.id,
            }
        }
        url = f'/api/authors/{author_2.id}/inbox/'
        self.client.force_authenticate(user=self.remote_node)
        response = self.client.post(url, data=payload, format="json")
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
    
    def test_IsRemotePostOnly_does_not_allow_remote_non_post_requests(self):
        author_1 = Author.objects.create(username="author_1", display_name="author_1")
        author_2 = Author.objects.create(username="author_2", display_name="author_2")

        Follow.objects.create(follower=author_1, followee=author_2)
        fr = FollowRequest.objects.create(sender=author_2, receiver=author_1)
        
        post = Post.objects.create(
            author=author_2,
            title="Post 1",
            description="Sample description",
            visibility="FRIENDS",
            content_type="text/plain",
            content="What's up people?"
        )

        # author_1 should see the new post from author_2 and the follow request from author_2
        Inbox.objects.create(target_author=author_1, post=post)
        Inbox.objects.create(target_author=author_1, follow_request_received=fr)
        
        url = f'/api/authors/{author_1.id}/inbox/'
        self.client.force_authenticate(user=self.remote_node)
        response = self.client.get(url)
        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)
    
    def test_is_remote_post_only_allows_all_local_requests(self):
        author_1 = Author.objects.create(username="author_1", display_name="author_1")
        author_2 = Author.objects.create(username="author_2", display_name="author_2")

        Follow.objects.create(follower=author_1, followee=author_2)
        fr = FollowRequest.objects.create(sender=author_2, receiver=author_1)
        
        post = Post.objects.create(
            author=author_2,
            title="Post 1",
            description="Sample description",
            visibility="FRIENDS",
            content_type="text/plain",
            content="What's up people?"
        )

        # author_1 should see the new post from author_2 and the follow request from author_2
        Inbox.objects.create(target_author=author_1, post=post)
        Inbox.objects.create(target_author=author_1, follow_request_received=fr)
        
        url = f'/api/authors/{author_1.id}/inbox/'
        self.client.force_authenticate(user=author_1)
        response = self.client.get(url)
        self.assertEqual(status.HTTP_200_OK, response.status_code)

class LikePostProcessorTestCase(APITestCase):
    
    def test_create_like_and_update_inbox(self):
        author_1 = Author.objects.create(username="author_1", display_name="author_1")
        author_2 = Author.objects.create(username="author_2", display_name="author_2")
        
        post_1 = Post.objects.create(
            author =author_2,
            title="Test Post",
            description="Testing post",
            source="source",
            origin="origin",
            unlisted=False,
            content_type= "text/plain",
            content="Some content",
            visibility= "PUBLIC"
        )
        
        payload = {
            "type": "like",
            "author": {
                "url": f'http://127.0.0.1:5054/authors/{author_1.id}/',
                "id": author_1.id,
            },
            "post":{
                'id':post_1.id,
                'author':{
                    "url": f'http://127.0.0.1:5054/authors/{author_2.id}/',
                    "id":author_2.id,                   
                }
            }
        }
        self.assertEqual(0, Like.objects.count())
        url = f'/api/authors/{author_2.id}/inbox/'
        self.client.force_authenticate(user=mock.Mock())
        response = self.client.post(url, data=payload, format="json")
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        self.assertEqual(1, Like.objects.count())
        like = Like.objects.first()
        self.assertEqual(author_1, like.author)
        self.assertEqual(post_1,like.post)
        self.assertEqual(1, Inbox.objects.count())
        inbox = Inbox.objects.first()
        self.assertEqual(author_2, inbox.target_author)
        self.assertEqual(like,inbox.like)
    
    def test_can_only_like_post_once(self):
        author_1 = Author.objects.create(username="author_1", display_name="author_1")
        author_2 = Author.objects.create(username="author_2", display_name="author_2")
        post_1 = Post.objects.create(
            author =author_2,
            title="Test Post",
            description="Testing post",
            source="source",
            origin="origin",
            unlisted=False,
            content_type= "text/plain",
            content="Some content",
            visibility= "PUBLIC"
        )
        Like.objects.create(author=author_1,post=post_1)
        self.assertEqual(1, Like.objects.count())
        payload = {
            "type": "like",
            "author": {
                "url": f'http://127.0.0.1:5054/authors/{author_1.id}/',
                "id": author_1.id,
            },
            "post":{
                'id':post_1.id,
                "author":{
                    "url": f'http://127.0.0.1:5054/authors/{author_2.id}/',
                    "id":author_2.id, 
                }
            }
        }
        url = f'/api/authors/{author_2.id}/inbox/'
        self.client.force_authenticate(user=mock.Mock())
        response = self.client.post(url, data=payload, format="json")
        self.assertEqual(1, Like.objects.count())
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)
    
    def test_like_not_valid_when_required_fields_are_not_given(self):
        """Proper serializer fields need to be given"""
        author_1 = Author.objects.create(username="author_1", display_name="author_1")
        author_2 = Author.objects.create(username="author_2", display_name="author_2")
        post_1 = Post.objects.create(
            author =author_2,
            title="Test Post",
            description="Testing post",
            source="source",
            origin="origin",
            unlisted=False,
            content_type= "text/plain",
            content="Some content",
            visibility= "PUBLIC"
        )
        # author field is missing in the post 
        payload = {
            "type": "like",
            "author": {
                "url": f'http://127.0.0.1:5054/authors/{author_1.id}/',
                "id": author_1.id,
            },
            "post":{
                'id':post_1.id,    
            }
        }
       
        url = f'/api/authors/{author_2.id}/inbox/'
        self.client.force_authenticate(user=mock.Mock())
        response = self.client.post(url, data=payload, format="json")
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)
        self.assertEqual(0, Like.objects.count())
                          
class AuthorLikedViewTestCase(APITestCase):
    def test_get_liked_posts(self):
        author_1 = Author.objects.create(username="author_1", display_name="author_1")
        author_2 = Author.objects.create(username="author_2", display_name="author_2")
        post_1 = Post.objects.create(
            author =author_2,
            title="Test Post",
            description="Testing post",
            source="source",
            origin="origin",
            unlisted=False,
            content_type= "text/plain",
            content="Some content",
            visibility= "PUBLIC"
        )
        post_2 = Post.objects.create(
            author=author_2,
            title="Post 2",
            description="Sample description 2",
            visibility="PUBLIC",
            content_type="text/plain",
            content="Public service announcement"
        )

        Like.objects.create(author=author_1,post=post_1)
        Like.objects.create(author=author_1,post=post_2)
        url = f'/api/authors/{author_1.id}/liked/'
        self.client.force_authenticate(user=mock.Mock())
        response = self.client.get(url,format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]['author']['id'],str(author_1.id))
        self.assertEqual(response.data[1]['author']['id'],str(author_1.id))
        self.assertEqual(response.data[0]['post'],f'http://testserver/api/authors/{str(author_1.id)}/posts/{str(post_1.id)}/')
        self.assertEqual(response.data[1]['post'],f'http://testserver/api/authors/{str(author_1.id)}/posts/{str(post_2.id)}/')
    
    def test_get_liked_public_posts_only(self):
        author_1 = Author.objects.create(username="author_1", display_name="author_1")
        author_2 = Author.objects.create(username="author_2", display_name="author_2")
        author_3 = Author.objects.create(username="author_3", display_name="author_3")
        post_1 = Post.objects.create(
            author =author_2,
            title="Post 1",
            description="Testing post",
            visibility= "PUBLIC",
            content="Testing Post 1"
        )
        post_2 = Post.objects.create(
            author=author_2,
            title="Post 2",
            description="Testing post 2",
            visibility="PRIVATE",
            content="Testing post 2"
        )
        post_3 = Post.objects.create(
            author=author_3,
            title="Post 3",
            visibility="FRIENDS",
            description="Testing post 3"   
        )
        post_4 = Post.objects.create(
            author =author_2,
            title="Post 4",
            description="Testing post 4",
            content="Some content",
            visibility= "PUBLIC"
        )
        post_5 = Post.objects.create(
            author =author_2,
            title="Post 5",
            description="Testing post 5",
            content="Some content",
            visibility= "PRIVATE"
        )

        Like.objects.create(author=author_1,post=post_1)
        Like.objects.create(author=author_1,post=post_2)
        Like.objects.create(author=author_1,post=post_3)
        Like.objects.create(author=author_1,post=post_4)
        Like.objects.create(author=author_1,post=post_5)
        self.assertEqual(5,Like.objects.count())
        url = f'/api/authors/{author_1.id}/liked/'
        self.client.force_authenticate(user=mock.Mock())
        response = self.client.get(url,format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]['author']['id'],str(author_1.id))
        self.assertEqual(response.data[1]['author']['id'],str(author_1.id))
        self.assertEqual(response.data[0]['post'],f'http://testserver/api/authors/{str(author_1.id)}/posts/{str(post_1.id)}/')
        self.assertEqual(response.data[1]['post'],f'http://testserver/api/authors/{str(author_1.id)}/posts/{str(post_4.id)}/')

    def test_only_get_posts_liked_by_author(self):
        # the purpose of this test is to ensure that authors/AUTHOR_ID/liked is not returning all authors that liked posts
        author_1 = Author.objects.create(username="author_1", display_name="author_1")
        author_2 = Author.objects.create(username="author_2", display_name="author_2")
        author_3 = Author.objects.create(username="author_3", display_name="author_3")
        author_4 = Author.objects.create(username="author_4", display_name="author_4")
        post = Post.objects.create(
            author =author_4,
            title="Post 1",
            description="Testing post",
            visibility= "PUBLIC",
            content="Testing Post 1"
        )
        
        Like.objects.create(author=author_1,post=post)
        Like.objects.create(author=author_2,post=post)
        Like.objects.create(author=author_3,post=post)
        url = f'/api/authors/{author_1.id}/liked/'
        self.client.force_authenticate(user=mock.Mock())
        response = self.client.get(url,format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['author']['id'],str(author_1.id))

    def test_no_posts_liked(self):
        author_1 = Author.objects.create(username="author_1", display_name="author_1")
        url = f'/api/authors/{author_1.id}/liked/'
        self.client.force_authenticate(user=mock.Mock())
        response = self.client.get(url,format="json")
        self.assertEqual(len(response.data),0)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

class PostLikesViewTestCase(APITestCase):
    def test_get_likes(self):
        author_1 = Author.objects.create(username="author_1", display_name="author_1")
        author_2 = Author.objects.create(username="author_2", display_name="author_2")
        author_3 = Author.objects.create(username="author_3", display_name="author_3")
        author_4 = Author.objects.create(username="author_4", display_name="author_4")
        author_5 = Author.objects.create(username="author_5", display_name="author_5")
        author_6 = Author.objects.create(username="author_6", display_name="author_6")
        post_1 = Post.objects.create(
            author =author_1,
            title="Post 1",
            description="Testing post",
            visibility= "PUBLIC",
            content="Testing Post 1"
        )
        Like.objects.create(author=author_1,post=post_1)
        Like.objects.create(author=author_2,post=post_1)
        Like.objects.create(author=author_3,post=post_1)
        Like.objects.create(author=author_4,post=post_1)
        Like.objects.create(author=author_5,post=post_1)
        Like.objects.create(author=author_6,post=post_1)
        self.assertEqual(6,Like.objects.count())
        url = f'/api/authors/{author_1.id}/posts/{post_1.id}/likes/'
        self.client.force_authenticate(user=mock.Mock())
        response = self.client.get(url,format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]['author']['id'],str(author_1.id))
        self.assertEqual(response.data[1]['author']['id'],str(author_2.id))
        self.assertEqual(response.data[2]['author']['id'],str(author_3.id))
        self.assertEqual(response.data[3]['author']['id'],str(author_4.id))
        self.assertEqual(response.data[4]['author']['id'],str(author_5.id))
        self.assertEqual(response.data[5]['author']['id'],str(author_6.id))
        self.assertEqual(response.data[0]['post'],f'http://testserver/api/authors/{str(author_1.id)}/posts/{str(post_1.id)}/')
        self.assertEqual(response.data[1]['post'],f'http://testserver/api/authors/{str(author_2.id)}/posts/{str(post_1.id)}/')
        self.assertEqual(response.data[2]['post'],f'http://testserver/api/authors/{str(author_3.id)}/posts/{str(post_1.id)}/')
        self.assertEqual(response.data[3]['post'],f'http://testserver/api/authors/{str(author_4.id)}/posts/{str(post_1.id)}/')
        self.assertEqual(response.data[4]['post'],f'http://testserver/api/authors/{str(author_5.id)}/posts/{str(post_1.id)}/')
        self.assertEqual(response.data[5]['post'],f'http://testserver/api/authors/{str(author_6.id)}/posts/{str(post_1.id)}/')
    
    def test_post_has_no_likes(self):
        author_1 = Author.objects.create(username="author_1", display_name="author_1")
        post_1 = Post.objects.create(
            author =author_1,
            title="Post 1",
            description="Testing post",
            visibility= "PUBLIC",
            content="Testing Post 1"
        )
        url = f'/api/authors/{str(author_1.id)}/posts/{str(post_1.id)}/likes/'
        self.client.force_authenticate(user=author_1)
        self.client.force_authenticate(user=mock.Mock())
        response = self.client.get(url,format="json")
        self.assertEqual(len(response.data),0)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
