from django.urls import path
from . import views
from .views import(
    AuthorDetailView,
    AuthorsView,
    AuthorRegistrationView,
    LoginView,
    LogoutView,
    PostView,
    AllPosts
)

# first argument, endpoint, second argument is the view that calling the url will send the request to

urlpatterns = [
    path('authors/', AuthorsView.as_view()),
    path('authors/<int:pk>/', AuthorDetailView.as_view(), name='author-detail'),
    path('register/', AuthorRegistrationView.as_view()),
    path('login/', LoginView.as_view()),
    path('logout/', LogoutView.as_view()),
    path('authors/<int:pk>/posts/<int:post_id>/',PostView.as_view()),
    path('authors/<int:pk>/posts/',AllPosts.as_view())
]