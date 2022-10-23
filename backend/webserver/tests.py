from ast import In
from django.test import TestCase
from webserver.models import Author, FollowRequest, Inbox, Post, Inbox, Follow
from rest_framework.test import APITestCase
from rest_framework import status
from unittest import mock
import datetime
import json
from django.utils.timezone import utc


class AuthorTestCase(TestCase):
    def test_author_creation(self):
        Author.objects.create(display_name="Mark",username ="mmcgoey")
        Author.objects.create(display_name="Author2",username="auth2")
        author_mark = Author.objects.get(display_name ="Mark")
        self.assertEqual(author_mark.username,"mmcgoey")
        author_two = Author.objects.get(username="auth2")
        self.assertEqual(author_two.display_name,"Author2")


class FollowRequestTestCase(TestCase):
    def test_follow_request_deletion(self):
        """When sender is deleted, the associated follow request is also deleted"""
        author1 = Author.objects.create(display_name="Mark",username ="mmcgoey")
        author2 = Author.objects.create(display_name="Author2",username="auth2")
        FollowRequest.objects.create(sender=author1,receiver=author2)
        
        self.assertEqual(FollowRequest.objects.count(),1)
        author1.delete()
        self.assertEqual(FollowRequest.objects.count(), 0)


class AuthorsViewTestCase(APITestCase):
    def test_requests_require_authentication(self):
        """TODO"""
        pass

    def test_get(self):
        # create some authors
        Author.objects.create(username="author_1", display_name="author_1")
        Author.objects.create(username="author_2", display_name="author_2")
        Author.objects.create(username="author_3", display_name="author_3")
        
        url = "/api/authors/"
        self.client.force_authenticate(user=mock.Mock())
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)
        author_1 = response.data[0]
        self.assertEqual(author_1["display_name"], "author_1")

class AuthorDetailView(APITestCase):
    def test_requests_require_authentication(self):
        """TODO"""
        pass
        
        
    def test_get(self):
        author_1 = Author.objects.create(username="author_1", display_name="author_1")
        url = f'/api/authors/{author_1.id}/'
        self.client.force_authenticate(user=mock.Mock())
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["display_name"], "author_1")
    
    def test_get_404(self):
        """If an author requested does not exist, should return 404"""
        fake_id = 500124540593854
        url = f'/api/authors/{fake_id}/'
        self.client.force_authenticate(user=mock.Mock())
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        
    
    def test_post_all_fields(self):
        """POST request works on all editable data fields"""
        author_1 = Author.objects.create()
        url = f'/api/authors/{author_1.id}/'
        self.client.force_authenticate(user=mock.Mock())
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
        self.client.force_authenticate(user=mock.Mock())
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
        self.client.force_authenticate(user=mock.Mock())
        response = self.client.post(url,data=payload)
        self.assertEqual(response.data["display_name"], "Mark McGoey")
        self.assertEqual(response.data["profile_image"], "")
        self.assertEqual(response.data["github_handle"], "mmcgoey")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        
    
    def test_post_404(self):
        """If an author to be updated does not exist, should return 404"""
        fake_id = 500124540593854
        url = f'/api/authors/{fake_id}/'
        payload = {
            "display_name": "Mark McGoey",
            "profile_image": "No image",
            "github_handle": "mmcgoey"
        }
        self.client.force_authenticate(user=mock.Mock())
        response = self.client.post(url,data=payload)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_post_non_editable_fields(self):
        author_1 = Author.objects.create()
        url = f'/api/authors/{author_1.id}/'
        new_id = 500124540593854
        new_url = f'/api/authors/{new_id}/'
        payload = {
            "id":new_id,
            "url":new_url
        }
        self.client.force_authenticate(user=mock.Mock())
        response = self.client.post(url,data=payload)
        
        self.assertEqual(response.data["id"], author_1.id)
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
        self.assertEqual(author_1, inbox.follow_request_sender)
    
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
        fr = FollowRequest.objects.last()
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
        self.assertTrue(fr1['url'].endswith('/authors/2/'))
        self.assertEqual(author_2.id, fr1['id'])
        self.assertEqual(author_3.id, fr2['id'])

    def test_author_has_no_follow_requests(self):
        author_1 = Author.objects.create(username="author_1", display_name="author_1")
        url = f'/api/authors/{author_1.id}/follow-requests/'
        self.client.force_authenticate(user=mock.Mock())
        response = self.client.get(url)

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(0, len(response.data))

    def test_author_does_not_exist(self):
        author_1 = Author.objects.create(username="author_1", display_name="author_1")
        url = f'/api/authors/{author_1.id + 1}/follow-requests/'
        self.client.force_authenticate(user=mock.Mock())
        response = self.client.get(url)
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
        self.assertEqual(test_author["id"], author_1.id)
        self.assertNotEqual(response.data["created_at"], None)
        self.assertEqual(response.data["title"], "Test Post")
        self.assertEqual(response.data["description"], "Testing post")
        self.assertEqual(response.data["source"], "source")
        self.assertEqual(response.data["origin"], "origin")
        self.assertEqual(response.data["unlisted"], False)
        self.assertEqual(response.data["content_type"], "text/plain")
        self.assertEqual(response.data["content"], "Some content")
        self.assertEqual(response.data["visibility"], "PUBLIC")
    
    def test_cannot_get_private_post(self):
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
            visibility= "PRIVATE"
        )

        url = f'/api/authors/{author_1.id}/posts/{post_1.id}/'
        self.client.force_authenticate(user=mock.Mock())
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
    def test_cannot_get_friends_post(self):
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
            visibility= "FRIENDS"
        )

        url = f'/api/authors/{author_1.id}/posts/{post_1.id}/'
        self.client.force_authenticate(user=mock.Mock())
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)   

    def test_get_404(self):
        author_1 = Author.objects.create(username="author_1", display_name="author_1")
        fake_post_id = 590385093845945
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
        response = self.client.post("/login/", data=request_payload, format="json")
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
        self.assertEqual(response.data["title"], "Mark McGoey")
        self.assertEqual(response.data["description"], "new description")
        self.assertEqual(response.data["unlisted"], True)
        self.assertEqual(response.data["content"], "Some new content")


    def test_non_editable_fields(self):
        author_1 = Author.objects.create() 
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
        self.client.force_authenticate(user=mock.Mock())
        payload = {
            "source":"new source",
            "origin": "new origin",  
            "visibility":"FRIENDS"  
        }
        self.client.post(url,data=payload)
        response = self.client.get(url,format=json)
        
        self.assertEqual(response.data["origin"], "origin")
        self.assertEqual(response.data["visibility"], "PUBLIC")
        self.assertEqual(response.data["source"], "source")
        
    

    def test_delete(self):
        author_1 = Author.objects.create(username="author_1", display_name="author_1")
        author_1.set_password("pass123")
        author_1.save()
        request_payload = {"username": "author_1", "password": "pass123"}
        self.client.post("/login/", data=request_payload, format="json")
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
    
    def test_cannot_delete_another_authors_post(self):
        author_1 = Author.objects.create(username="author_1", display_name="author_1")
        author_2 = Author.objects.create(username="author_2", display_name="author_2")
        author_2.set_password("pass123")
        author_2.save()
        request_payload = {"username": "author_2", "password": "pass123"}
        self.client.post("/login/", data=request_payload, format="json")
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
        self.assertEqual(Post.objects.filter(author=author_1.id).count(),1)
        response = self.client.delete(url)
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)
        self.assertEqual(Post.objects.filter(author=author_1.id).count(),1)

    def test_cannot_edit_another_authors_post(self):
        author_1 = Author.objects.create(username="author_1", display_name="author_1")
        author_2 = Author.objects.create(username="author_2", display_name="author_2")
        author_2.set_password("pass123")
        author_2.save()
        request_payload = {"username": "author_2", "password": "pass123"}
        self.client.post("/login/", data=request_payload, format="json")
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
        self.client.post("/login/", data=request_payload, format="json")
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
        self.client.post("/login/", data=request_payload, format="json")
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
        self.client.post("/login/", data=request_payload, format="json")
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
        self.client.post("/login/", data=request_payload, format="json")
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
        self.client.post("/login/", data=request_payload, format="json")
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
 
    def test_send_friend_post_to_inbox(self):
        author_1 = Author.objects.create(username="author_1", display_name="author_1")
        author_1.set_password("pass123")
        author_1.save()
        request_payload = {"username": "author_1", "password": "pass123"}
        self.client.post("/login/", data=request_payload, format="json")
        author_2 = Author.objects.create(username="author_2", display_name="author_2")
        author_3 = Author.objects.create(username="author_3", display_name="author_3")
        author_4 = Author.objects.create(username="author_4", display_name="author_4")
        author_5 = Author.objects.create(username="author_5", display_name="author_5")
        Follow.objects.create(follower=author_2,followee=author_1)
        Follow.objects.create(follower=author_3,followee=author_1)
        Follow.objects.create(follower=author_4,followee=author_1)
        Follow.objects.create(follower=author_5,followee=author_1)
        payload = {
            "title": "Mark McGoey",
            "description": "new description",
            "unlisted":True,
            "content":"Some new content",
            "visibility":"FRIENDS",
            "content_type":"text/plain"
        }
        url = f'/api/authors/{author_1.id}/posts/'
        self.client.force_authenticate(user=author_1)
        response = self.client.post(url,data=payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        inbox = Inbox.objects.first()
        self.assertEqual(author_2, inbox.target_author)
        self.assertEqual(4, Inbox.objects.count())
        self.assertEqual(payload["title"], inbox.post.title)
        self.assertEqual(payload["description"], inbox.post.description)
        self.assertEqual(payload["visibility"], inbox.post.visibility)
        self.assertEqual(payload["content_type"], inbox.post.content_type)

    def test_send_private_post_to_inbox(self):
        author_1 = Author.objects.create(username="author_1", display_name="author_1")
        author_1.set_password("pass123")
        author_1.save()
        request_payload = {"username": "author_1", "password": "pass123"}
        self.client.post("/login/", data=request_payload, format="json")
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
        inbox = Inbox.objects.first()
        self.assertEqual(author_2, inbox.target_author)
        self.assertEqual(payload["title"],inbox.post.title)
        self.assertEqual(payload["description"],inbox.post.description)
        self.assertEqual(payload["unlisted"],inbox.post.unlisted)
        self.assertEqual(payload["visibility"],inbox.post.visibility)
        self.assertEqual(payload["content_type"],inbox.post.content_type)

    def test_cannot_create_new_posts_for_other_authors(self):
        author_1 = Author.objects.create(username="author_1", display_name="author_1")
        author_2 = Author.objects.create(username="author_2", display_name="author_2")
        author_2.set_password("pass123")
        author_2.save()
        request_payload = {"username": "author_2", "password": "pass123"}
        self.client.post("/login/", data=request_payload, format="json") 
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
        self.client.post("/login/", data=request_payload, format="json") 
       

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
        self.client.post("/login/", data=request_payload, format="json") 
       

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
        self.client.post("/login/", data=request_payload, format="json")
        
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

    
    
   


    