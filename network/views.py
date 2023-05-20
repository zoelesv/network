from django.contrib.auth import authenticate, login, logout, get_user_model
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django.core.paginator import Paginator
from .models import User, Post, Follow
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from datetime import datetime
from django.contrib.auth.models import User

def index(request):

    if request.user.username:
        user = request.user.username
        # for a POST method, add a new post in Post
        if request.method == "POST":
            newpost = Post()
            User = get_user_model()
            user = User.objects.get(username=user)
            newpost.user = user
            now = datetime.now()
            newpost.timestamp = now.strftime(" %d %B %Y %X ")
            newpost.post = request.POST.get("new-post")
            #insert the new post to the database
            newpost.save()
            return redirect('index')
    # Show all posts in order
    posts = Post.objects.all().order_by('-timestamp')
    paginator = Paginator(posts, 10)
    if request.GET.get("page") != None:
        try:
            posts = paginator.page(request.GET.get("page"))
        except:
            posts = paginator.page(1)
    else:
        posts = paginator.page(1)
    return render(request, "network/index.html", {'posts': posts})


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            User = get_user_model()
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")

@login_required
def profile(request, username):
    User = get_user_model()
    username = User.objects.get(username=username)
    button = "Follow" if Follow.objects.filter(follower=request.user, following=username).count() == 0 else "Unfollow"

    if request.method == "POST":
        if request.POST["button"] == "Follow":
            button = "Unfollow"
            Follow.objects.create(follower=request.user, following=username)
        else:
            button = "Follow"
            Follow.objects.get(follower=request.user, following=username).delete()

    posts = Post.objects.filter(user=username).order_by('-timestamp')
    paginator = Paginator(posts, 10)
    if request.GET.get("page") != None:
        try:
            posts = paginator.page(request.GET.get("page"))
        except:
            posts = paginator.page(1)
    else:
        posts = paginator.page(1)
    #for i in users_profile.follower.all():
        #print(i)
    return render(request, 'network/profile.html',{
        "username": username,
        "followers": Follow.objects.filter(following=username).count(),
        "following": Follow.objects.filter(follower=username).count(),
        'posts': posts,
        "button": button
    })

@login_required
def following(request):
    following = Follow.objects.filter(follower=request.user).values('following_id')
    posts = Post.objects.filter(user__in=following).order_by('-timestamp')
    paginator = Paginator(posts, 10)
    if request.GET.get("page") != None:
        try:
            posts = paginator.page(request.GET.get("page"))
        except:
            posts = paginator.page(1)
    else:
        posts = paginator.page(1)
    return render(request, 'network/following.html', {'posts': posts})


@login_required
@csrf_exempt
def like(request):
    if request.method == "POST":
        post_id = request.POST.get('id')
        is_liked = request.POST.get('is_liked')
        try:
            post = Post.objects.get(id=post_id)
            if is_liked == 'no':
                post.like.add(request.user)
                is_liked = 'yes'
            elif is_liked == 'yes':
                post.like.remove(request.user)
                is_liked = 'no'
            post.save()

            return JsonResponse({'like_count': post.like.count(), 'is_liked': is_liked, "status": 201})
        except:
            return JsonResponse({'error': "Post not found", "status": 404})
    return JsonResponse({}, status=400)


@login_required
@csrf_exempt
def edit(request):
    if request.method == "POST":
        post_id = request.POST.get('id')
        new_post = request.POST.get('post')
        try:
            post = Post.objects.get(id=post_id)
            if post.user == request.user:
                post.post = new_post.strip()
                post.save()
                return JsonResponse({}, status=201)
        except:
            return JsonResponse({}, status=404)

    return JsonResponse({}, status=400)


