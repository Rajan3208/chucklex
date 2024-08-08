from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views
from .views import like_post  # Import the like_post view

urlpatterns = [
    path('', views.index, name='index'),
    path('settings/', views.settings, name='settings'),
    path('upload/', views.upload, name='upload'),
    path('follow/', views.follow,  name='follow'),
    path('search/', views.search,  name='search'),
    path('save_post/', views.save_post, name='save_post'),
    path('api/post/<str:post_id>/', views.get_post_details, name='get_post_details'),
    path('profile/<str:pk>/', views.profile, name='profile'),
    path('like-post/', views.like_post, name='like-post'),# Use the imported like_post view
    path('signup/', views.signup, name='signup'),
    path('create_story/', views.create_story, name='create_story'),
    path('view_story/<int:story_id>/', views.view_story, name='view_story'),
    path('signin/', views.signin, name='signin'),
    path('logout/', views.logout, name='logout'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
