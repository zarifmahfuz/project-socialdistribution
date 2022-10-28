"""social_distribution URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from django.urls import path, include
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', TemplateView.as_view(template_name='home.html')),
    path('profile/<str:profileId>', login_required(TemplateView.as_view(template_name='profile.html'), redirect_field_name=None)),
    path('profile/<str:profileId>/followers/', login_required(TemplateView.as_view(template_name='followers.html'), redirect_field_name=None)),
    path('register/', auth_views.LoginView.as_view(redirect_authenticated_user=True, template_name='register.html')),
    path('login/', auth_views.LoginView.as_view(redirect_authenticated_user=True, template_name='login.html')),
    path('logout/', login_required(TemplateView.as_view(template_name='logout.html'), redirect_field_name=None)),
    path('create-post/', login_required(TemplateView.as_view(template_name='createPost.html'), redirect_field_name=None)),
    path('edit-post/<int:profileId>/<int:postId>', login_required(TemplateView.as_view(template_name='editPost.html'), redirect_field_name=None)),
    path('view-post/<int:profileId>/<int:postId>', login_required(TemplateView.as_view(template_name='viewPost.html'), redirect_field_name=None)),
    path('inbox/', login_required(TemplateView.as_view(template_name='inbox.html'), redirect_field_name=None)),
    path('api/', include('webserver.urls')),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]
