from hmac import new
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User, auth
from django.contrib import messages
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from .models import Profile, Post, LikePost, FollowersCount
from itertools import chain
import random
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from .models import SavedPost
from django.http import JsonResponse
from django.core.files.uploadedfile import InMemoryUploadedFile
from PIL import Image
import io
import json
from django.views.decorators.http import require_GET
from .models import Post, LikePost, Profile
from django.utils import timezone
from .models import Story
from django.db.models import Max
from django.utils import timezone
from itertools import groupby
from operator import attrgetter
from django.db.models import Max, Q  


@login_required(login_url='signin')
def index(request):
    user_object = User.objects.get(username=request.user.username)
    user_profile, created = Profile.objects.get_or_create(user=user_object, defaults={'id_user': user_object.id})

    user_following = FollowersCount.objects.filter(follower=request.user.username)
    user_following_list = [user.user for user in user_following]

    if user_following.exists():
        feed = [Post.objects.filter(user=username) for username in user_following_list]
        feed_list = list(chain(*feed))
        show_welcome = False
    else:
        feed_list = []
        show_welcome = True

    # Attach user profiles to the posts
    for post in feed_list:
        post.user_profile = Profile.objects.get(user__username=post.user)

    active_stories = Story.objects.filter(
        Q(user__username__in=user_following_list) | Q(user=request.user),
        expires_at__gt=timezone.now()
    ).order_by('-created_at')
    
    all_users = User.objects.all()
    new_suggestions_list = [x for x in all_users if (x.username not in user_following_list and x.username != request.user.username)]
    random.shuffle(new_suggestions_list)

    suggestions_username_profile_list = []
    for user in new_suggestions_list[:4]:
        try:
            profile = Profile.objects.get(user=user)
            followers_count = FollowersCount.objects.filter(user=user).count()
            suggestions_username_profile_list.append({
                'profile': profile,
                'followers_count': followers_count
            })
        except Profile.DoesNotExist:
            pass

    return render(request, 'index.html', {
        'user_profile': user_profile,
        'posts': feed_list,
        'show_welcome': show_welcome,
        'suggestions_username_profile_list': suggestions_username_profile_list,
        'active_stories': active_stories,
    })






        
@login_required(login_url='signin')
def upload(request):
    if request.method == 'POST':
        user = request.user.username
        image = request.FILES.get('image_upload')
        caption = request.POST['caption']

        new_post = Post.objects.create(user=user, image=image, caption=caption)
        new_post.save()

        return redirect('/')
    else:
        return redirect('/')

@login_required(login_url='signin')
def search(request):
    user_object = User.objects.get(username=request.user.username)
    user_profile = Profile.objects.get(user=user_object)
    
    if request.method == 'POST':
        username = request.POST['username']
        username_object = User.objects.filter(username__icontains=username)
        
        username_profile_list = []
        
        for user in username_object:
            profile_list = Profile.objects.filter(user=user)
            username_profile_list.extend(profile_list)
            
        return render(request, 'search.html', {'user_profile': user_profile, 'username_profile_list': username_profile_list})
    else:
        return redirect('/')

@login_required(login_url='signin')
def create_story(request):
    if request.method == 'POST':
        content = request.FILES.get('story_content')
        if content:
            Story.objects.create(user=request.user, content=content)
    return redirect('index')


@login_required(login_url='signin')
def view_story(request, story_id):
    story = get_object_or_404(Story, id=story_id)
    data = {
        'id': story.id,
        'user': story.user.username,
        'content_url': story.content.url,
        'created_at': story.created_at.isoformat(),
        'expires_at': story.expires_at.isoformat(),
    }
    return JsonResponse(data)


def like_post(request):
    post_id = request.GET.get('post_id')
    
    if not request.user.is_authenticated:
        # Store the post_id in the session for redirecting after login
        request.session['redirect_after_login'] = f'/?post_id={post_id}'
        messages.info(request, 'Please log in to like posts.')
        return redirect('signin')
    
    username = request.user.username
    post = get_object_or_404(Post, id=post_id)
    like_filter = LikePost.objects.filter(post_id=post_id, username=username).first()
    
    if like_filter is None:
        new_like = LikePost.objects.create(post_id=post_id, username=username)
        post.no_of_likes += 1
        post.save()
    else:
        like_filter.delete()
        post.no_of_likes -= 1
        post.save()
    
    return redirect('/')

@login_required(login_url='signin')
def get_post_details(request, post_id):
    try:
        post = Post.objects.get(id=post_id)
        user_profile = Profile.objects.get(user__username=post.user)
        likes_count = LikePost.objects.filter(post_id=post_id).count()
        comments = []  # You'll need to implement a Comment model and fetch comments here
        
        data = {
            'id': str(post.id),
            'user': post.user,
            'profile_image': user_profile.profileimg.url,
            'image_url': post.image.url,
            'caption': post.caption,
            'created_at': post.created_at.strftime("%B %d, %Y, %I:%M %p"),
            'likes_count': likes_count,
            'comments': comments,
        }
        return JsonResponse(data)
    except Post.DoesNotExist:
        return JsonResponse({'error': 'Post not found'}, status=404)
@csrf_exempt
@require_POST
def save_post(request):
    data = json.loads(request.body)
    post_id = data.get('post_id')
    user = request.user
    post = get_object_or_404(Post, id=post_id)
    
    saved_post, created = SavedPost.objects.get_or_create(user=user, post=post)
    
    if created:
        return JsonResponse({'status': 'success', 'message': 'Post saved successfully'})
    else:
        saved_post.delete()
        return JsonResponse({'status': 'success', 'message': 'Post unsaved successfully'})

@login_required(login_url='signin')
def profile(request, pk):
    user_object = get_object_or_404(User, username=pk)
    user_profile = get_object_or_404(Profile, user=user_object)
    user_posts = Post.objects.filter(user=user_object)
    user_post_length = user_posts.count()
    
    follower = request.user.username
    user = pk
    
    if FollowersCount.objects.filter(follower=follower, user=user).first():
        button_text = 'Unfollow'
    else:
        button_text = 'Follow'
        
    user_followers = FollowersCount.objects.filter(user=user_object).count()
    user_following = FollowersCount.objects.filter(follower=user_object).count()
    
    # Get saved posts
    saved_posts = SavedPost.objects.filter(user=user_object)
        
    context = {
        'user_object': user_object,
        'user_profile': user_profile,
        'user_posts': user_posts,
        'user_post_length': user_post_length,
        'button_text': button_text, 
        'user_followers': user_followers,
        'user_following': user_following,
        'saved_posts': saved_posts ,
        'user_posts': [{'id': str(post.id), 'image': post.image.url} for post in user_posts],# Add this line
    }
    return render(request, 'profile.html', context)

@login_required(login_url='signin')
def follow(request):
    if request.method == 'POST':
        follower = request.POST['follower']
        user = request.POST['user']
        
        if FollowersCount.objects.filter(follower=follower, user=user).exists():
            delete_follower = FollowersCount.objects.get(follower=follower, user=user)
            delete_follower.delete()
        else:
            new_follower = FollowersCount.objects.create(follower=follower, user=user)
            new_follower.save()
        
        return redirect('/profile/' + user)
    else:
        return redirect('/')

@login_required(login_url='signin')
def settings(request):
    user_profile = Profile.objects.get(user=request.user)

    if request.method == 'POST':
        # Handle cover image
        if 'cover_image' in request.FILES:
            cover_image = request.FILES['cover_image']
            img = Image.open(cover_image)
            img = img.convert('RGB')
            
            # Calculate dimensions to crop the image to 1128:191 aspect ratio
            img_width, img_height = img.size
            aspect_ratio = 1128 / 191
            
            if img_width / img_height > aspect_ratio:
                new_height = img_height
                new_width = int(new_height * aspect_ratio)
                left = (img_width - new_width) // 2
                top = 0
                right = left + new_width
                bottom = img_height
            else:
                new_width = img_width
                new_height = int(new_width / aspect_ratio)
                left = 0
                top = (img_height - new_height) // 2
                right = img_width
                bottom = top + new_height
            
            img = img.crop((left, top, right, bottom))
            img = img.resize((2256, 382), Image.LANCZOS)
            
            output = io.BytesIO()
            img.save(output, format='JPEG', quality=85)
            output.seek(0)
            
            user_profile.coverimg = InMemoryUploadedFile(output, 'ImageField', 
                                                         f"{cover_image.name.split('.')[0]}.jpg", 
                                                         'image/jpeg', 
                                                         output.getbuffer().nbytes, None)

        # Handle profile image
        if 'image' in request.FILES:
            profile_image = request.FILES['image']
            user_profile.profileimg = profile_image

        # Handle bio and location
        user_profile.bio = request.POST.get('bio', '')
        user_profile.location = request.POST.get('location', '')

        user_profile.save()
        return redirect('settings')

    return render(request, 'setting.html', {'user_profile': user_profile})
def signup(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        password2 = request.POST['password2']

        if password == password2:
            if User.objects.filter(email=email).exists():
                messages.info(request, 'Email Taken')
                return redirect('signup')
            elif User.objects.filter(username=username).exists():
                messages.info(request, 'Username Taken')
                return redirect('signup')
            else:
                user = User.objects.create_user(username=username, email=email, password=password)
                user.save()

                user_login = auth.authenticate(username=username, password=password)
                auth.login(request, user_login)

                user_model = User.objects.get(username=username)
                new_profile = Profile.objects.create(user=user_model, id_user=user_model.id)
                new_profile.save()
                return redirect('settings')
        else:
            messages.info(request, 'Passwords do not match')
            return redirect('signup')
    else:
        return render(request, 'signup.html')

def signin(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = auth.authenticate(username=username, password=password)

        if user is not None:
            auth.login(request, user)
            # Check if there's a redirect URL in the session
            redirect_url = request.session.pop('redirect_after_login', '/')
            return redirect(redirect_url)
        else:
            messages.info(request, 'Credentials Invalid')
            return redirect('signin')
    else:
        return render(request, 'signin.html')

@login_required(login_url='signin')
def logout(request):
    auth.logout(request)
    return redirect('signin')