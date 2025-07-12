from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from .models import *
from .forms import *
from django.contrib.auth.decorators import login_required
from django.db.models import Q


def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect("dashboard")
        else:
            messages.error(request, "Invalid credentials")
    return render(request, "login.html")

def signup(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm = request.POST.get("confirm_password")
        profile_image = request.FILES.get("profile_image")

        if password != confirm:
            messages.error(request, "Passwords do not match")
        elif User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken")
        else:
            user = User.objects.create_user(username=username, email=email, password=password)
            user.save()
            user_profile = user.userprofile
            if profile_image:
                user_profile.profile_image = profile_image
            user_profile.save()
            login(request, user)
            return redirect("dashboard")

    return render(request, "signup.html")


def logout_view(request):
    logout(request)
    return redirect("login")


@login_required
def dashboard(request):
    form = IdeaForm()
    ideas = Idea.objects.all().order_by('-timestamp')

    liked_idea_ids = Like.objects.filter(user=request.user).values_list('idea_id', flat=True)
    following_user_ids = Follow.objects.filter(follower=request.user).values_list('following_id', flat=True)

    if request.method == "POST":
        form = IdeaForm(request.POST, request.FILES)
        if form.is_valid():
            idea = form.save(commit=False)
            idea.user = request.user
            idea.save()
            Notification.objects.create(
                recipient=request.user,
                content=f"Your idea '{idea.title}' was posted successfully."
            )
            return redirect('dashboard')

    return render(request, 'dashboard.html', {
        'form': form,
        'ideas': ideas,
        'liked_idea_ids': liked_idea_ids,
        'following_user_ids': following_user_ids,
    })


@login_required
def like_idea(request, idea_id):
    idea = get_object_or_404(Idea, id=idea_id)
    like, created = Like.objects.get_or_create(user=request.user, idea=idea)
    if not created:
        like.delete()
    else:
        if request.user != idea.user:
            Notification.objects.create(
                recipient=idea.user,
                content=f"{request.user.username} liked your idea: {idea.title}"
            )
    return redirect('dashboard')

@login_required
def comment_on_idea(request, idea_id):
    idea = get_object_or_404(Idea, id=idea_id)
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.idea = idea
            comment.user = request.user
            comment.save()
            if request.user != idea.user:
                Notification.objects.create(
                    recipient=idea.user,
                    content=f"{request.user.username} commented on your idea: {idea.title}"
                )
    return redirect('dashboard')

@login_required
def follow_unfollow(request, user_id):
    target = get_object_or_404(User, id=user_id)
    follow, created = Follow.objects.get_or_create(follower=request.user, following=target)
    if not created:
        follow.delete()
    else:
        Notification.objects.create(
            recipient=target,
            content=f"{request.user.username} started following you."
        )
    return redirect('dashboard')


@login_required
def profile(request):
    user = request.user
    profile = user.userprofile
    ideas = Idea.objects.filter(user=user)
    
    follower_count = Follow.objects.filter(following=user).count()
    following_count = Follow.objects.filter(follower=user).count()
    post_count = ideas.count()

    return render(request, 'profile.html', {
        'user': user,
        'profile': profile,
        'ideas': ideas,
        'follower_count': follower_count,
        'following_count': following_count,
        'post_count': post_count,
    })

@login_required
def search_community(request):
    users = User.objects.exclude(id=request.user.id)  # or add filters later
    return render(request, 'search.html', {'users': users})


@login_required
def chat_system(request, user_id=None):
    users = User.objects.exclude(id=request.user.id)
    active_user = None
    messages = []

    if user_id:
        active_user = User.objects.get(id=user_id)
        messages = ChatMessage.objects.filter(
            Q(sender=request.user, receiver=active_user) |
            Q(sender=active_user, receiver=request.user)
        )

    if request.method == "POST" and active_user:
        msg = request.POST.get("message")
        if msg:
            ChatMessage.objects.create(sender=request.user, receiver=active_user, message=msg)
            return redirect('chat_user', user_id=active_user.id)

    return render(request, "chat.html", {
        'users': users,
        'messages': messages,
        'active_user': active_user,
    })

@login_required
def notifications_view(request):
    notifications = Notification.objects.filter(recipient=request.user).order_by('-timestamp')
    # Mark unseen notifications as seen
    notifications.filter(seen=False).update(seen=True)

    return render(request, 'notifications.html', {
        'notifications': notifications,
    })
    
    
@login_required
def edit_idea(request, idea_id):
    idea = get_object_or_404(Idea, id=idea_id, user=request.user)
    if request.method == "POST":
        form = IdeaForm(request.POST, request.FILES, instance=idea)
        if form.is_valid():
            form.save()
            messages.success(request, "Idea updated successfully.")
            return redirect("dashboard")
    else:
        form = IdeaForm(instance=idea)
    return render(request, "edit_idea.html", {'form': form, 'idea': idea})


@login_required
def delete_idea(request, idea_id):
    idea = get_object_or_404(Idea, id=idea_id, user=request.user)
    if request.method == "POST":
        idea.delete()
        messages.success(request, "Idea deleted successfully.")
        return redirect("dashboard")
    return render(request, "confirm_delete.html", {'idea': idea})
