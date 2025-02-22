CMPUT404-project-socialdistribution
===================================

[14Degrees](https://social-distribution-14degrees.herokuapp.com/), a distributed social networking app designed to help you find connections within 14 degrees of separation.

## List of Contents:
* [Remote Connections](https://github.com/zarifmahfuz/project-socialdistribution#remote-connections)
* [New features developed since Project Presentation](https://github.com/zarifmahfuz/project-socialdistribution#additions-made-since-project-presentation)
* Local Setup -
  * [Backend Setup](https://github.com/zarifmahfuz/project-socialdistribution#setup)
  * [Frontend Setup](https://github.com/zarifmahfuz/project-socialdistribution/tree/master/frontend#running-the-front-end)
* [API Documentation](https://github.com/zarifmahfuz/project-socialdistribution#api-information)
  * [Sample uses for every API endpoint](https://github.com/zarifmahfuz/project-socialdistribution#sample-usage)
* [Planning & Design](https://github.com/zarifmahfuz/project-socialdistribution#planning--design)

Remote Connections
=================
Teams that we connected to:
1. Team 10 - https://socioecon.herokuapp.com/home/
2. Team 11 - https://cmsjmnet.herokuapp.com/
3. Team 14 - https://social-distribution-14degrees2.herokuapp.com/

Additions Made Since Project Presentation
=================
* Likes
![image](https://user-images.githubusercontent.com/45117618/206813324-3fcb19dd-4568-4119-a477-30afcf31cdd8.png)
* Comments (And Liking Comments)
![image](https://user-images.githubusercontent.com/45117618/206813299-bf261c7a-8be3-4d98-be2b-90a98fa0d731.png)
* Image Posts
![image](https://user-images.githubusercontent.com/45117618/206813271-c457604f-50fb-4fe3-9d93-e5c34fc190c4.png)
* Inbox
![image](https://user-images.githubusercontent.com/45117618/206813438-7966b83c-da36-4368-acb1-0b14bc13b8a9.png)
* Sharing Image Posts
![image](https://user-images.githubusercontent.com/45117618/206813538-759d8419-b221-418c-8dd7-8b1bf9005fed.png)

Setup
=================
## Database
If you would like to use a local Postgres DB instead of the default SQLite DB you need to do the following:
1. Have PostgreSQL server installed on your local machine
2. Enter into the PSQL console with `sudo -u postgres psql`
3. In the opened PSQL console run the following commands
    ```sql
    CREATE DATABASE social_distribution_14;
    CREATE USER team_14 WITH PASSWORD 'team14';
    ALTER USER team_14 WITH SUPERUSER;
    ```
4. You also need to set an environment variable to use Postgres - `export LOCAL_POSTGRESQL=true`

## Backend
1. Move into the backend directory of the repository: `cd backend`
2. Create an start a virtual environment:
```
python3 -m venv env
source env/bin/activate  # On Windows use `env\Scripts\activate`
```
3. Install dependencies
```
pip install -r requirements.txt
```
4. `cd backend && python manage.py migrate`

5. Run the webserver `python manage.py runserver`
  - You should be able to run the server on a **non-default port** by running something like `python manage.py runserver 5900`

### If you want to load some seed data
When asked for authentication enter any of the authors usernames with the password pass123
```
python manage.py flush   (if your database is not empty)
python manage.py loaddata fixtures/all_data.json
```

## How to Create Seed Data
1. At first, you can create any set of data of your liking through the list API routes or though the frontend.
2. Once you have inserted some meaningful data into your local database, you can dump the data into file fixtures. To do that make sure that you are in the Django project directory (`backend/`) and run the following commands -
```
python manage.py dumpdata webserver --indent 4 > mydata.json
```
This will create a file called `mydata.json` in your current working directory.

3. If you want, you can push this dataset in the `webserver/fixtures` directory of our Github repository.
4. To load this dataset to your local db at a later time, run the following commands -
```
python manage.py flush  # this will clear the current data in your db
python manage.py loaddata mydata.json
```
Now, you're all set!

API Information
=================
## API Endpoints
| Resource                  | POST                    | GET                           | PUT                                     | DELETE  |
| ------------------------- |:-------------:| -----:| -----:| -----:|
| /api/login/                | Logs in an author | - | - | - |
| /api/register/ | Registers a new author | - | - | - |
| /api/logout/                | Logs out an author  | - | - | - |
| /api/posts/                | - | Retrieves the list of public posts on the server (open to everyone) | - | - |
| /api/authors/                | - | **Retrieves the list of authors [A][R]** | - | - |
| /api/authors/<author_id>/                | Updates an author's profile [A] | **Retrieves an author's profile [A][R]** | - | - |
| /api/authors/<author_id>/inbox/              | **Creates a new inbox item for an author [A][R]**  | Retrieve's an author's inbox [A] | - | - |
| /api/authors/<author_id>/follow-requests/                | - | Retrives the list of follow requests for an author [A] | - | - |
| /api/authors/<author_id>/follow-requests/<foreign_author_id>/                | - | - | - | Decline a follow request[A] |
| /api/authors/<author_id>/followers/                | - | **Retrives the list of followers for an author [A][R]** | - | - |
| /api/authors/<author_id>/followers/<foreign_author_id>/                | - | Checks if foreign_author_id is a follower of author_id [A] | Accepts a follow request [A] | Removes a follower [A] |
| /api/authors/<author_id>/posts/               | Creates a new post for an author [A] | **Retrieves recent posts from an author [A][R]** | - | - |
| /api/authors/<author_id>/posts/<post_id>/                | Update an authors post [A] | **Retrieves an authors post [A][R]** | - | Delete an authors post [A] |
| /api/nodes/             | Add a node [Admin only] | - | - | - |
| /api/authors/<author_id>/posts/<post_id>/likes/                | - | **Retrieves a list of likes on an authors post [A][R]** | - | - |
| /api/authors/<author_id>/liked/                | - | **Retrieves a list of public things liked by an author [A][R]** | - | - |
| /api/authors/<author_id>/posts/<post_id>/image/                | - | **Retrieves an image [R]** | - | - |
| /api/authors/<author_id>/posts/<post_id>/comments/                | - | **Retrieves the comments for a post [A][R]** | - | - |
| /api/authors/<author_id>/posts/<post_id>/comments/<comment_id>/likes/                | - | **Retrieves the list of likes made on a comment [A][R]** | - | - |

### Notes
- [R] specifies that a remote request can be made to the route. In other words, only those routes marked with [R] accept remote requests. They have also been bolded for ease of navigability.
- [A] specifies that the request must be authenticated
- [WIP] specifies that some features of the endpoint is under development

## Sample Usage
### Register
#### Required fields
- `username`
- `password`
- `password2`
- `display_name`

#### Sample Request
<img width="1130" alt="image" src="https://user-images.githubusercontent.com/43586048/197074885-31cd313d-5d66-489c-81f2-8b69d4d89262.png">


#### Sample Response
```
{
    "username": "author532",
    "display_name": "good_author"
}
```

#### Possible Status Codes
- `201 Created`
- `400 Bad Request`


### Login
#### Required fields
- `username`
- `password`

#### Sample Request
![image](https://user-images.githubusercontent.com/43586048/197075454-33a87648-b4b6-49db-99e9-95591adf7b07.png)

#### Sample Response
```
{
    "message": "Login Success"
}
```

#### Possible Status Codes
- `200 OK`
- `400 Bad Request`
- `401 Unauthorized`


### Logout
#### Required fields
None

#### Sample Request
![image](https://user-images.githubusercontent.com/43586048/197075741-9e0a2256-029d-433e-b457-ae6bb93427e7.png)


#### Sample Response
```
{
    "message": "Successfully Logged out"
}
```

#### Possible Status Codes
- `200 OK`

### Retrieve all profiles on the server
#### Sample Request
<img width="1130" alt="image" src="https://user-images.githubusercontent.com/43586048/197076274-b535b9a4-880e-479a-9302-1c7cb97a9114.png">

#### Sample Response
```
[
    
    {
        "url": "http://127.0.0.1:8000/api/authors/6e3c2a39-8fef-4efb-bb98-0826a7f15f39/",
        "id": "6e3c2a39-8fef-4efb-bb98-0826a7f15f39",
        "display_name": "myuser",
        "profile_image": "",
        "github_handle": ""
    },
    {
        "url": "http://127.0.0.1:8000/api/authors/255c89fd-1b47-4f42-8a1b-5c574c6117f3/",
        "id": "255c89fd-1b47-4f42-8a1b-5c574c6117f3",
        "display_name": "author_1",
        "profile_image": "",
        "github_handle": ""
    }

]
```

#### Possible Status Codes
- `200 OK`
- `401 Unauthorized`

### Retrieve an author's profile
#### Sample Request
<img width="1130" alt="image" src="https://user-images.githubusercontent.com/77307203/201427306-fb7a6317-e637-4842-aa0f-a1c84b448700.png">

#### Sample Response
```
{
    "url": "http://127.0.0.1:8000/api/authors/6e3c2a39-8fef-4efb-bb98-0826a7f15f39/",
    "id": "6e3c2a39-8fef-4efb-bb98-0826a7f15f39",
    "display_name": "myuser",
    "profile_image": "",
    "github_handle": ""
}
```

#### Possible Status Codes
- `200 OK`
- `401 Unauthorized`
- `404 Not Found`


### Update an author's profile
#### Sample Request
<img width="1130" alt="image" src="https://user-images.githubusercontent.com/77307203/201429443-026c2974-c330-4a39-8fcc-0c299e809d15.png">

#### Sample Response
```
{
    "url": "http://127.0.0.1:8000/api/authors/6e3c2a39-8fef-4efb-bb98-0826a7f15f39/",
    "id": "6e3c2a39-8fef-4efb-bb98-0826a7f15f39",
    "display_name": "noob_author",
    "profile_image": "",
    "github_handle": ""
}
```

#### Possible Status Codes
- `200 OK`
- `401 Unauthorized`
- `404 Not Found`

### Send a follow request
#### Sample Request
<img width="1130" alt="image" src="https://user-images.githubusercontent.com/77307203/201431979-ef4c8fda-f667-479a-9beb-c9f7eb0ae2df.png">

**Note**: You may wonder why the author `url`s are needed with the request payload. This is needed for project part 2 to differentiate between a local author and a remote one. If an author is a remote one, we will forward the follow request to it's matching remote server.

#### Sample Response
```
{
    "message": "OK"
}
```

#### Possible Status Codes
- `201 Created`
- `400 Bad Request`
- `401 Unauthorized`
- `404 Not Found`
- `409 Conflict`: This can come up when you try to re-send a follow request when the request is still pending

### Retrieve the list of follow requests for an author
#### Sample Request
<img width="1130" alt="image" src="https://user-images.githubusercontent.com/77307203/201432901-9aca2c78-8476-4ab4-928b-02e068c2a3c2.png">

#### Sample Response
```
[
    {
        "url": "http://127.0.0.1:8000/api/authors/6e3c2a39-8fef-4efb-bb98-0826a7f15f39/",
        "id": "6e3c2a39-8fef-4efb-bb98-0826a7f15f39",
        "display_name": "noob_author",
        "profile_image": "",
        "github_handle": ""
    },
    {
        "url": "http://127.0.0.1:8000/api/authors/edcfedc2-0c39-40e9-94de-7d234ebf408e/",
        "id": "edcfedc2-0c39-40e9-94de-7d234ebf408e",
        "display_name": "author_Z",
        "profile_image": "",
        "github_handle": ""
    }
]
```

#### Possible Status Codes
- `200 OK`
- `401 Unauthorized`
- `404 Not Found`

### Accept a follow request
#### Sample Request
Author with id 255c89fd-1b47-4f42-8a1b-5c574c6117f3 accepts a follow request of author with id 6e3c2a39-8fef-4efb-bb98-0826a7f15f39 -
<img width="1131" alt="image" src="https://user-images.githubusercontent.com/77307203/201437124-7a4517cf-4874-4411-945d-c6c2a62c625b.png">

#### Sample Response
```
{
    "message": "OK"
}
```

#### Possible Status Codes
- `201 Created`
- `400 Bad Request`: This can be returned under a few different circumstances - when a matching follow request does not exist, when valid request payload is not given, or when an authors try to follow themselves
- `401 Unauthorized`
- `404 Not Found`


### Decline a follow request
#### Sample Request
<img width="1134" alt="image" src="https://user-images.githubusercontent.com/77307203/201437722-642ee340-3ea1-429e-a842-dc8d49148347.png">

#### Sample Response
```
{
    "message": "Follow request declined"
}
```

#### Possible Status Codes
- `200 OK`: means follow request was declined
- `400 Bad Request`
- `401 Unauthorized`
- `404 Not Found`: can be returned when a matching follow request does not exist


### Remove a follower
#### Sample Request
<img width="1134" alt="image" src="https://user-images.githubusercontent.com/77307203/201438215-811e72f8-89ee-4565-961d-beff14421448.png">


#### Sample Response
```
{
    "message": "follower removed"
}
```

#### Possible Status Codes
- `200 OK`
- `400 Bad Request`
- `401 Unauthorized`
- `404 Not Found`: this can be returned when a matching follower can't be found

### Check if an author is following some other author
#### Sample Usage
<img width="1131" alt="image" src="https://user-images.githubusercontent.com/77307203/201438520-d2b1eddd-6123-4d35-b5af-061985e7d734.png">

#### Sample Response
```
{
    "message": "edcfedc2-0c39-40e9-94de-7d234ebf408e is not a follower of 255c89fd-1b47-4f42-8a1b-5c574c6117f3"
}
```

**Note:** We can update the response messages over time if requested.

#### Possible Status Codes
- `200 OK`: this is returned when a matching follower specified by the resource url was found.
- `401 Unauthorized`
- `404 Not Found`: this is returned when a matching follower is not found

### Retrieve a list of all the followers for an author
#### Sample Usage
Retrieve the list of followers for author_id 255c89fd-1b47-4f42-8a1b-5c574c6117f3 -
<img width="1131" alt="image" src="https://user-images.githubusercontent.com/77307203/201439314-4f66c384-da9d-40b2-8af1-43ac7e62e080.png">

#### Sample Response
```
[
    {
        "url": "http://127.0.0.1:8000/api/authors/6e3c2a39-8fef-4efb-bb98-0826a7f15f39/",
        "id": "6e3c2a39-8fef-4efb-bb98-0826a7f15f39",
        "display_name": "noob_author",
        "profile_image": "",
        "github_handle": ""
    }
]
```

#### Possible Status Codes
- `200 OK`
- `401 Unauthorized`
- `404 Not Found`

### Retrieve an author's inbox
#### Sample Usage
Retrieve the inbox of author with id  255c89fd-1b47-4f42-8a1b-5c574c6117f3-
<img width="1131" alt="image" src="https://user-images.githubusercontent.com/77307203/201439818-92d90dd9-266e-43aa-b67b-bad649000fd2.png">

#### Sample Response
```
[
    {
        "sender": {
            "url": "http://127.0.0.1:8000/api/authors/edcfedc2-0c39-40e9-94de-7d234ebf408e/",
            "id": "edcfedc2-0c39-40e9-94de-7d234ebf408e",
            "display_name": "noob_author",
            "profile_image": "",
            "github_handle": ""
        },
        "type": "follow"
    },
    {
        "author": {
            "url": "http://127.0.0.1:8000/api/authors/edcfedc2-0c39-40e9-94de-7d234ebf408e/",,
            "id": "edcfedc2-0c39-40e9-94de-7d234ebf408e",
            "display_name": "noob_author",
            "profile_image": "",
            "github_handle": ""
        },
        "created_at": "2022-10-23T03:25:09.184425Z",
        "edited_at": null,
        "title": "Post 1",
        "description": "Sample description",
        "source": "",
        "origin": "",
        "unlisted": false,
        "content_type": "text/plain",
        "content": "What's up people?",
        "visibility": "FRIENDS",
        "type": "post"
    }
]
```

Notes:
- The `type` field will be present in each inbox item. This specifies the type of the inbox. Possible values: `"post"` for a new post, `"follow"` for a follow request

#### Possible Status Codes
- `200 OK`
- `401 Unauthorized`
- `404 Not Found`


### Retrieve a list of all the posts for an author
#### Sample Usage
Retrieve the list of posts for author id 255c89fd-1b47-4f42-8a1b-5c574c6117f3 -
<img width="1131" alt="image" src="https://user-images.githubusercontent.com/77307203/201440910-ed6fcf78-5b3c-4fc9-b216-39ced68b6f6e.png">

#### Sample Response
```
[
    {
        "author": {
            "url": "http://localhost:8000/api/authors/255c89fd-1b47-4f42-8a1b-5c574c6117f3/",
            "id": 255c89fd-1b47-4f42-8a1b-5c574c6117f3,
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
        "unlisted": false,
        "content_type": "text/plain",
        "content": "change the content",
        "visibility": "PUBLIC",
        "likes_count": 2
    }

]
```

#### Possible Status Codes
- `200 OK`
- `401 Unauthorized`
- `404 Not Found`

### Create a new post
#### Sample Usage
Author with id 255c89fd-1b47-4f42-8a1b-5c574c6117f3 creates a new post-
<img width="1131" alt="image" src="https://user-images.githubusercontent.com/77307203/201441059-e6ca2998-031a-4fb6-97bf-299b31745511.png">

#### Sample Response
```
[
   {
    "id": "824fbe15-4e6b-42b0-8bce-eadfc2914f26",
    "title": "My first post",
    "description": "My first post",
    "unlisted": false,
    "content": "some content",
    "visibility": "PUBLIC",
    "content_type": "text/plain"
    }
]
```

#### Possible Status Codes
- `201 Created`
- `400 Bad Request`
- `401 Unauthorized`
- `404 Not Found`

### Retrieve an authors post
#### Sample Usage
Retrieve the post for author id 255c89fd-1b47-4f42-8a1b-5c574c6117f3 with post id 824fbe15-4e6b-42b0-8bce-eadfc2914f26 -
<img width="1131" alt="image" src="https://user-images.githubusercontent.com/77307203/201441409-01220585-0f22-4c9a-be57-83f8194a4e5c.png">


#### Sample Response
```
[
  {
    "id": "824fbe15-4e6b-42b0-8bce-eadfc2914f26",
    "author": {
        "url": "http://127.0.0.1:8000/api/authors/255c89fd-1b47-4f42-8a1b-5c574c6117f3/",
        "id": "255c89fd-1b47-4f42-8a1b-5c574c6117f3",
        "display_name": "author_1",
        "profile_image": "",
        "github_handle": ""
    },
    "created_at": "2022-11-11T22:39:45.407227Z",
    "edited_at": null,
    "title": "My first post",
    "description": "My first post",
    "source": "",
    "origin": "",
    "unlisted": false,
    "content_type": "text/plain",
    "content": "some content",
    "visibility": "PUBLIC",
    "likes_count": 0
    }
]
```

#### Possible Status Codes
- `200 OK`
- `401 Unauthorized`
- `404 Not Found`
- `400 Bad Request`

### Update an authors post
#### Sample Usage
Update the post for author id 255c89fd-1b47-4f42-8a1b-5c574c6117f3 with post id 824fbe15-4e6b-42b0-8bce-eadfc2914f26 -
<img width="1131" alt="image" src="https://user-images.githubusercontent.com/77307203/201441897-53e8146c-39c9-40ad-82ef-61f25f7516aa.png">


#### Sample Response
```
[
  {
    "id": "824fbe15-4e6b-42b0-8bce-eadfc2914f26",
    "title": "update my post title",
    "description": "update my post description",
    "unlisted": false,
    "content": "some updated content"
    }
]
```

#### Possible Status Codes
- `200 OK`
- `401 Unauthorized`
- `404 Not Found`
- `400 Bad Request`

### Delete an authors post
#### Sample Usage
Delete the post for author id 255c89fd-1b47-4f42-8a1b-5c574c6117f3 with post id  824fbe15-4e6b-42b0-8bce-eadfc2914f26-
<img width="1131" alt="image" src="https://user-images.githubusercontent.com/77307203/201442124-fed4ffca-d28e-42f8-9c08-5f0be03a7b9e.png">

#### Sample Response
```
[
    {
        "message": "Object deleted!"
    }
]
```
#### Possible Status Codes
- `200 OK`
- `401 Unauthorized`
- `404 Not Found`
- `400 Bad Request`

### Retrieve a list of likes on an authors post
#### Sample Usage
Retreive a list of likes on author with id 255c89fd-1b47-4f42-8a1b-5c574c6117f3 post with post id 9b050b09-97d1-44b7-89ec-d2ed2c23cde1 -
<img width="1131" alt="image" src="https://user-images.githubusercontent.com/77307203/201504699-434390ce-e11f-42b4-a138-a641b9f2e132.png">

#### Sample Response
```json
[
    {
        "author": {
            "url": "http://127.0.0.1:8000/api/authors/6e3c2a39-8fef-4efb-bb98-0826a7f15f39/",
            "id": "6e3c2a39-8fef-4efb-bb98-0826a7f15f39",
            "display_name": "cjenkins123",
            "profile_image": "",
            "github_handle": "cashj45"
        },
        "post": "http://127.0.0.1:8000/api/authors/6e3c2a39-8fef-4efb-bb98-0826a7f15f39/posts/9b050b09-97d1-44b7-89ec-d2ed2c23cde1/",
        "object": "http://127.0.0.1:8000/api/authors/6e3c2a39-8fef-4efb-bb98-0826a7f15f39/posts/9b050b09-97d1-44b7-89ec-d2ed2c23cde1/"
    },
    {
        "author": {
            "url": "http://127.0.0.1:8000/api/authors/edcfedc2-0c39-40e9-94de-7d234ebf408e/",
            "id": "edcfedc2-0c39-40e9-94de-7d234ebf408e",
            "display_name": "UltimateBeast123",
            "profile_image": "",
            "github_handle": "ultimateBeast"
        },
        "post": "http://127.0.0.1:8000/api/authors/edcfedc2-0c39-40e9-94de-7d234ebf408e/posts/9b050b09-97d1-44b7-89ec-d2ed2c23cde1/",
        "object": "http://127.0.0.1:8000/api/authors/edcfedc2-0c39-40e9-94de-7d234ebf408e/posts/9b050b09-97d1-44b7-89ec-d2ed2c23cde1/"
    }    
]
```
* The `author` represents the author who liked the post

#### Possible Status Codes
- `200 OK`
- `401 Unauthorized`
- `404 Not Found`

### Retrieve a list of likes made by an author
#### Sample Usage
<img width="977" alt="image" src="https://user-images.githubusercontent.com/43586048/205526251-4f351e77-80dd-409d-82d7-d2b83b29a433.png">


#### Sample Response
```json
[
    {
        "author": {
            "url": "http://127.0.0.1:8014/api/authors/2cd3cfe1-c56d-45aa-8640-79ffa40f7e3d/",
            "id": "2cd3cfe1-c56d-45aa-8640-79ffa40f7e3d",
            "display_name": "john",
            "profile_image": "",
            "github_handle": ""
        },
        "comment": "http://127.0.0.1:8014/api/authors/30558702-f634-4b24-bfa6-4bd25ab441c5/posts/595b9f1f-0053-4f44-ad88-aac59f2a6da2/comments/afd4bd59-188a-4100-9599-37b26f5e50c8/",
        "object": "http://127.0.0.1:8014/api/authors/30558702-f634-4b24-bfa6-4bd25ab441c5/posts/595b9f1f-0053-4f44-ad88-aac59f2a6da2/comments/afd4bd59-188a-4100-9599-37b26f5e50c8/"
    },
    {
        "author": {
            "url": "http://127.0.0.1:8014/api/authors/2cd3cfe1-c56d-45aa-8640-79ffa40f7e3d/",
            "id": "2cd3cfe1-c56d-45aa-8640-79ffa40f7e3d",
            "display_name": "john",
            "profile_image": "",
            "github_handle": ""
        },
        "post": "http://127.0.0.1:8014/api/authors/2cd3cfe1-c56d-45aa-8640-79ffa40f7e3d/posts/595b9f1f-0053-4f44-ad88-aac59f2a6da2/",
        "object": "http://127.0.0.1:8014/api/authors/2cd3cfe1-c56d-45aa-8640-79ffa40f7e3d/posts/595b9f1f-0053-4f44-ad88-aac59f2a6da2/"
    }
]
```

#### Possible Status Codes
- `200 OK`
- `401 Unauthorized`
- `404 Not Found`

### Like a post
#### Sample Usage
Author with id 442352d0-f10a-4ac9-a42b-55c2f41179b3 likes post 9b050b09-97d1-44b7-89ec-d2ed2c23cde1 made by author with id 255c89fd-1b47-4f42-8a1b-5c574c6117f3 
<img width="1131" alt="image" src="https://user-images.githubusercontent.com/77307203/201505623-aead299a-3766-4b66-bea4-f7a363d06f35.png">

#### Sample Response
```
{
    "message": "OK"
}
```

#### Possible Status Codes
- `201 Created`
- `400 Bad Request`
- `401 Unauthorized`
- `404 Not Found`

### Like a comment
#### Sample Usage
![image](https://user-images.githubusercontent.com/43586048/205526447-32f23c55-73e6-4338-a9a8-edce643f5336.png)

* Send the request at the inbox route of the comment's owner
* The `author` field represents the author liking the post

#### Possible Status Codes
- `201 Created`
- `400 Bad Request`
- `401 Unauthorized`
- `404 Not Found`

### Send a post to an author's inbox
#### Sample Usage
<img width="1128" alt="image" src="https://user-images.githubusercontent.com/43586048/202331501-bd40933e-2624-4774-954d-ccece26fae43.png">


#### Sample Response
Same as updating other types of inboxes.

#### Possible Status Codes
- `201 Created`
- `400 Bad Request`
- `401 Unauthorized`
- `404 Not Found`

### Create an Image Post
Understand how image posts are meant to be used from [this eclass forum post](https://eclass.srv.ualberta.ca/mod/forum/discuss.php?d=2136532).

#### Sample Usage
<img width="1012" alt="image" src="https://user-images.githubusercontent.com/43586048/205419794-fa9a5831-6657-4d22-8a35-f1d637218318.png">

* Uses the regular post creation route
* Required payload fields -
  * `content_type`: specify either "image/jpeg;base64" or "image/png;base64"
  * `image`: enter the base64 encoded image string
* Optional payload fields (just here to satisfy requirements) -
  * `unlisted`: default value is `true` so that image posts do not show up on the feed by themselves (if they did, then the base64 encoded strings would show up in the `content` field of the post). 
  * `visibility`: image posts are "PUBLIC" by default so that they are globally accessible by their url. I would keep the visibility to public for all image posts so that remote nodes can also fetch them to render images in their corresponding markdown.

#### Sample Response
```
{
    "id": "f5a85964-3dc8-4d30-84da-17bac1f7f5fe",
    "url": "http://127.0.0.1:8014/api/authors/c134c50a-76d7-498e-b55e-b7cff72936db/posts/f5a85964-3dc8-4d30-84da-17bac1f7f5fe/image/"
}
```

You will be able to access the image at the url specified -
<img width="1428" alt="image" src="https://user-images.githubusercontent.com/43586048/205419946-adbf139e-7ed1-4c14-8662-600cda52a7b5.png">

**You can use the provided url to set the value of the `src` attribute of an `<img>` tag to embed an image within a post.**

#### Potential Status Codes
Same as a regular post creation.

### Retrieve an image
#### Sample Request
Send a GET request to a url such as `http://127.0.0.1:8014/api/authors/c134c50a-76d7-498e-b55e-b7cff72936db/posts/f5a85964-3dc8-4d30-84da-17bac1f7f5fe/image/`
* The `post_id` provided has to be the ID of the image post

#### Sample Response
<img width="1010" alt="image" src="https://user-images.githubusercontent.com/43586048/205420797-e51d2414-1678-4e31-b07f-855b212a3761.png">

#### Potential Status Codes
- `200 OK`
- `404 Not Found`
- `400 Bad Request` - this can be returned if you are unauthorized to view the image


### Create a comment
#### Sample Request
![image](https://user-images.githubusercontent.com/43586048/205478141-6d824847-795b-4d0d-a1de-c5a50b153a3b.png)

* Use the inbox route of the post's author to create a comment
* The top-level `author` field represents the author who is making the comment
* The nested `author` field represents the author of the post
* `content_type` is optional and has a default value of "text/plain"

#### Sample Response
```json
{
    "message": "OK"
}
```

#### Potential Status Codes
- `201 Created`
- `400 Bad Request`
- `404 Not Found`

Additionally, here's how the comment inbox would look like if you send a GET request to the author's inbox -
```json
[
    {
        "author": {
            "url": "http://127.0.0.1:8014/api/authors/ee87c0c2-2eda-4071-859e-8aeff3638231/",
            "id": "ee87c0c2-2eda-4071-859e-8aeff3638231",
            "display_name": "hugh",
            "profile_image": "",
            "github_handle": ""
        },
        "comment": "Awesome post!",
        "content_type": "text/plain",
        "created_at": "2022-12-04T06:38:13.906331Z",
        "id": "http://127.0.0.1:8014/api/authors/30558702-f634-4b24-bfa6-4bd25ab441c5/posts/595b9f1f-0053-4f44-ad88-aac59f2a6da2/comments/afd4bd59-188a-4100-9599-37b26f5e50c8/",
        "type": "comment"
    }
]
```


### View comments
#### Sample Request
If the post is not PUBLIC, only the post's author can fetch comments from this route.
<img width="1010" alt="image" src="https://user-images.githubusercontent.com/43586048/205511911-5612cfe5-fe27-4940-85d1-3486162183f8.png">

#### Sample Response
```json
[
    {
        "author": {
            "url": "http://127.0.0.1:8014/api/authors/ee87c0c2-2eda-4071-859e-8aeff3638231/",
            "id": "ee87c0c2-2eda-4071-859e-8aeff3638231",
            "display_name": "hugh",
            "profile_image": "",
            "github_handle": ""
        },
        "comment": "Awesome post!",
        "content_type": "text/plain",
        "created_at": "2022-12-04T06:38:13.906331Z",
        "id": "http://127.0.0.1:8014/api/authors/30558702-f634-4b24-bfa6-4bd25ab441c5/posts/595b9f1f-0053-4f44-ad88-aac59f2a6da2/comments/afd4bd59-188a-4100-9599-37b26f5e50c8/"
    }
]
```

#### Potential Status Codes
- `200 Ok`
- `401 Unauthorized`
- `403 Forbidden` - this returned when you are authenticated but not allowed to get comments from this post
- `404 Not Found`

Comments will also be associated with their corresponding posts in the following format -
```json
[
    {
        "id": "595b9f1f-0053-4f44-ad88-aac59f2a6da2",
        "author": {
            "url": "http://127.0.0.1:8014/api/authors/30558702-f634-4b24-bfa6-4bd25ab441c5/",
            "id": "30558702-f634-4b24-bfa6-4bd25ab441c5",
            "display_name": "cashJenkins",
            "profile_image": "",
            "github_handle": ""
        },
        "created_at": "2022-12-04T06:33:41.909944Z",
        "edited_at": null,
        "title": "Test post",
        "description": "Test description",
        "source": "",
        "origin": "",
        "unlisted": false,
        "content_type": "text/plain",
        "content": "Test content",
        "visibility": "PUBLIC",
        "likes_count": 0,
        "count": 1,
        "comments": "http://127.0.0.1:8014/api/authors/30558702-f634-4b24-bfa6-4bd25ab441c5/posts/595b9f1f-0053-4f44-ad88-aac59f2a6da2/comments",
        "comments_src": {
            "type": "comments",
            "page": 1,
            "size": 1,
            "comments": [
                {
                    "author": {
                        "url": "http://127.0.0.1:8014/api/authors/ee87c0c2-2eda-4071-859e-8aeff3638231/",
                        "id": "ee87c0c2-2eda-4071-859e-8aeff3638231",
                        "display_name": "hugh",
                        "profile_image": "",
                        "github_handle": ""
                    },
                    "comment": "Awesome post!",
                    "content_type": "text/plain",
                    "created_at": "2022-12-04T06:38:13.906331Z",
                    "id": "http://127.0.0.1:8014/api/authors/30558702-f634-4b24-bfa6-4bd25ab441c5/posts/595b9f1f-0053-4f44-ad88-aac59f2a6da2/comments/afd4bd59-188a-4100-9599-37b26f5e50c8/"
                }
            ]
        }
    }
]
```

* Notice the newly added fields that are related to comments - `count`, `comments`, `comments_src`
* At most 5 comments will be returned with a post (ordered by most recent comments first)
* Keep in mind that comments will not be returned with all posts
  * Comments will always be returned with public posts
  * If the post is not public, comments will only be returned if the request is made by the author of the post

## Pagination
### Retrieve a paginated list of authors
#### Sample Request
![image](https://user-images.githubusercontent.com/43586048/197662427-57359a86-43d4-4b2b-a7ba-b37f3ede8be1.png)

#### Sample Response
```
{
    "count": 27,
    "next": "http://localhost:8000/api/authors/?page=2&size=5",
    "previous": null,
    "results": [
        {
            "url": "http://localhost:8000/api/authors6e3c2a39-8fef-4efb-bb98-0826a7f15f39/",
            "id": "6e3c2a39-8fef-4efb-bb98-0826a7f15f39",
            "display_name": "",
            "profile_image": "",
            "github_handle": ""
        },
        {
            "url": "http://localhost:8000/api/authors/255c89fd-1b47-4f42-8a1b-5c574c6117f3/",
            "id": "255c89fd-1b47-4f42-8a1b-5c574c6117f3",
            "display_name": "zarif",
            "profile_image": "",
            "github_handle": ""
        },
        {
            "url": "http://localhost:8000/api/authors/edcfedc2-0c39-40e9-94de-7d234ebf408e/",
            "id": "edcfedc2-0c39-40e9-94de-7d234ebf408e",
            "display_name": "author_0_handle",
            "profile_image": "",
            "github_handle": ""
        },
        {
            "url": "http://localhost:8000/api/authors/442352d0-f10a-4ac9-a42b-55c2f41179b3/",
            "id": "442352d0-f10a-4ac9-a42b-55c2f41179b3",
            "display_name": "author_1_handle",
            "profile_image": "",
            "github_handle": ""
        },
        {
            "url": "http://localhost:8000/api/authors/e6573c76-6916-45c9-af94-0d8130b8ec1f/",
            "id": e6573c76-6916-45c9-af94-0d8130b8ec1f,
            "display_name": "author_2_handle",
            "profile_image": "",
            "github_handle": ""
        }
    ]
}
```

#### Notes
- Use the `page` query parameter to specify the page you would like to fetch. If you just specify the `page` query param without the `size`, a default size of 10 will be used
- Use the `size` query parameter to specify the size of the page. You cannot use this on it's one (you also need to pass the `page` query parameter).
- `count` specifies the total number of records available at this resource
- Send requests to the urls specified in `next` and `prev` to use the pagination


## Connecting to new nodes
### Add a node to connect with
#### Sample Request
<img width="1126" alt="image" src="https://user-images.githubusercontent.com/43586048/202946372-67256269-0012-45a5-8576-04fc7a49d2c8.png">

* `node_name`, `password`, `password2` are required authentication fields that will be used by external nodes to connect to us
* `auth_username`, `auth_password` are required authentication fields that will be used by our node to connect to external nodes
* `api_url` is base api url of the external node

#### Sample Response
![image](https://user-images.githubusercontent.com/43586048/201426000-1f0943cb-cba6-4fa8-8f31-81249a24ee46.png)

* The external node will need to authenticate themselves with `username:node_name` and `password:password`

Planning & Design
============
- You can view the [ER model for our app here](https://github.com/zarifmahfuz/project-socialdistribution/blob/master/docs/ERModelv2.png).
- You can view the [Figma designs for our UI here.](https://github.com/zarifmahfuz/project-socialdistribution/blob/master/docs/DESIGN.md)

Deployment
============
If you are added as collaborator on the Heroku app for this project, you should be able to access it here - https://dashboard.heroku.com/apps/social-distribution-14degrees. You are able to do pretty much any administration work on the Heroku app once you're added as a collaborator. Some examples of what you can do -
* You can manually deploy any branch on this repository from the [`Deploy` tab](https://dashboard.heroku.com/apps/social-distribution-14degrees/deploy/github)
* You can ssh into the production container/dyno with the command `heroku ps:exec --dyno=web.1 --app social-distribution-14degrees`
* You can ssh into a one-off (non-production) container/dyno with the command `heroku run bash -a social-distribution-14degrees`

Contributing
============

Send a pull request and be sure to update this file with your name.

Contributors / Licensing
========================

Generally everything is LICENSE'D under the Apache 2 license by Zarif Mahfuz.

All text is licensed under the CC-BY-SA 4.0 http://creativecommons.org/licenses/by-sa/4.0/deed.en_US

Contributors:

    Zarif Mahfuz
    Mark McGoey
    Chidubem Ogbudibe
    Timothee Legros
