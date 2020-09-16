from django.shortcuts import render, redirect
from .models import *
from django.contrib import messages
from django.db.models import Q
import bcrypt
import datetime

# --------------- LOGIN PAGE ----------------- #
def index(request):
    # if 'user_id' in request.session:
    #     return redirect('/dash')
    return render(request, 'index.html')

# --------------- REGISTER ----------------- #
def register(request):
    errors = User.objects.validator(request.POST)

    if len(errors) > 0:
        for key,value in errors.items():
            messages.error(request, value)
        return redirect("/")

    is_user_in_db = User.objects.filter(email=request.POST['email']).first()

    if is_user_in_db:
        print("user already exists")
        return redirect("/")

    hashed_pw = bcrypt.hashpw(
        request.POST['password'].encode(),
        bcrypt.gensalt()
        ).decode()

    user_created = User.objects.create(
        user_name = request.POST['user_name'],
        first_name = request.POST['first_name'],
        last_name = request.POST['last_name'],
        birthday = request.POST['birthday'],
        email = request.POST['email'],
        password = hashed_pw
    )
    friends_list = FriendsList.objects.create(user=user_created)

    request.session['user_id'] = user_created.id

    return redirect("/dash")

# --------------- LOGIN ----------------- #
def login(request):
    errors = User.objects.login_validator(request.POST)

    if len(errors) > 0:
        for key,value in errors.items():
            messages.error(request,value)
        return redirect("/")

    found_user = User.objects.filter(email=request.POST['email']).first()

    if found_user:
        is_pw_correct = bcrypt.checkpw(
            request.POST['password'].encode(), 
            found_user.password.encode()
    )
        if is_pw_correct:
            request.session['user_id'] = found_user.id
            return redirect('/dash')
        else:
            print("something is not working")
            return redirect("/")
    else:
        print("something is not working")
        return redirect("/")

    return redirect("/dash")

# --------------- DISPLAY DASHBOARD ----------------- #
def dashboard(request):
    if 'user_id' in request.session:
        user = User.objects.get(id=request.session['user_id'])
        user.logged_in = True
        user.save()
        
        friends_list = FriendsList.objects.get(user=user)
        friend_requests = FriendsList.objects.filter(friends=user).exclude(user=user)
        context = {
            "user" : user,
            "online_users" : User.objects.filter(logged_in=True),
            "all_stories" : Story.objects.all().order_by("-created_at"),
            "other_stories" : Story.objects.all().order_by("created_at"),
            "all_comments" : Comment.objects.all(),
            "friends_list": friends_list,
            "friend_requests": friend_requests,
            "online_users" : User.objects.filter(logged_in=True),
        }
    else:
        return redirect('/')
    return render(request, "dash.html", context)

# --------------- DISPLAY STORY ----------------- #
def display_share(request):
    if 'user_id' in request.session:
        user = User.objects.get(id=request.session['user_id'])
        context = {
            "user" : user,
        }
    else:
        return redirect('/')
    return render(request, "share.html", context)

# --------------- CREATE STORY ----------------- #
def create_share(request):
    Story.objects.create(
        who = request.POST['who'],
        desc = request.POST['desc'],
        story_img = request.FILES['story_img'],
        submitted_by = User.objects.get(id=request.session['user_id'])
    )
    return redirect("/dash")

# --------------- LIKE STORY ----------------- #
def like_story(request, id):
    story_id = Story.objects.get(id=id)
    user_id = request.session['user_id']

    s_added_like = story_id.user_likes.add(user_id)
    
    return redirect("/dash")

# --------------- UNLIKE STORY ----------------- #
def unlike_story(request, id):
    story_id = Story.objects.get(id=id)
    user_id = request.session['user_id']

    s_remove_like = story_id.user_likes.remove(user_id)

    return redirect("/dash")

# --------------- DELETE STORY ----------------- #
def delete(request, id):
    delete_story= Story.objects.get(id=id)
    delete_story.delete()
    return redirect("/dash")

# --------------- DELETE STORY FROM USER PAGE ----------------- #
def delete_two(request, id):
    delete_story= Story.objects.get(id=id)
    delete_story.delete()
    return redirect("/dash")

# --------------- POSTING COMMENTS ----------------- #
def post_comment(request):
    errors = Comment.objects.validator(request.POST)
    
    if len(errors) > 0:
        for key,value in errors.items():
            messages.error(request,value)
        return redirect("/dash")

    comment_created = Comment.objects.create(
        user=User.objects.get(id=request.session['user_id']),
        comment=request.POST['comment'],
        commented_story=Story.objects.get(id=request.POST['story_id'])
    )

    request.session['comment_id'] = comment_created.id
    return redirect("/dash")

# --------------- LIKE COMMENT ----------------- #
def like_comment(request, id):
    comment_id = Comment.objects.get(id=id)
    user_id = request.session['user_id']

    c_added_like = comment_id.c_user_likes.add(user_id)
    
    return redirect("/dash")

# --------------- UNLIKE COMMENT ----------------- #
def unlike_comment(request, id):
    comment_id = Comment.objects.get(id=id)
    user_id = request.session['user_id']

    c_remove_like = comment_id.c_user_likes.remove(user_id)

    return redirect("/dash")

# --------------- DELETE COMMENT ----------------- #
def delete_comment(request, id):
    delete_comment= Comment.objects.get(id=id)
    delete_comment.delete()
    return redirect("/dash")

# --------------- DISPLAY PROFILE PAGE ----------------- #
def user_page(request, username):
    if 'user_id' in request.session:
        user = User.objects.get(user_name=username)
        user_id = User.objects.get(id=request.session['user_id'])

        context = {
            "user" : user,
            "user_id" : user_id,
            "profile_story" : Story.objects.filter(submitted_by=user),
            "online_users" : User.objects.filter(logged_in=True),
            "all_comments" : Comment.objects.all(),
            "friends_list" : FriendsList.objects.get(user=user_id),
            "f" : FriendsList.objects.get(user=user),
        }
    else:
        return redirect('/')
    return render(request, "user_page.html", context)

# --------------- EDIT PROFILE PAGE ----------------- #
def edit_profile(request, username):
    if not request.FILES:
        messages.error(request, "Please select a photo.")
        return redirect(f'/profile/{username}')
    update_user = User.objects.get(id=request.session['user_id'])

    update_user.profile_pic = request.FILES["profile_pic"]
    update_user.save()

    return redirect(f'/profile/{username}')

# --------------- LOGOUT ----------------- #
def logout(request):
    user = User.objects.get(id=request.session['user_id'])
    user.logged_in = False
    user.save()
    request.session.clear()
    return redirect("/")

# --------------- MESSAGES ----------------- #
def user_messages(request):
    if 'user_id' not in request.session:
        return redirect('/user/login')
    user = User.objects.get(id=request.session['user_id'])
    unread_messages = Message.objects.filter(receiver=user, read=False)
    if 'user_search' in request.session:
        user_list = User.objects.filter(
            Q(first_name__icontains=request.session['user_search']) | Q(last_name__icontains=request.session['user_search']) | Q(user_name__icontains=request.session['user_search']))
        if not user_list:
            messages.error(
                request, '"' + request.session['user_search'] + '"' + " does not match any users.")
    else:
        user_list = User.objects.filter().exclude(id=user.id).order_by('last_name')
    if 'other_user' in request.session:
        other_user = User.objects.get(id=request.session['other_user'])
        user_messages = Message.objects.filter(
            sender__id=request.session['other_user'], receiver=user)
        chat_messages = Message.objects.filter(
            Q(sender__id=request.session['other_user'], receiver=user) | Q(sender=user, receiver__id=request.session['other_user'])).order_by('created_at')
        today = datetime.date.today()
        context = {
            "user": user,
            "other_user": other_user,
            "user_list": user_list,
            "user_messages": user_messages,
            "unread_messages": unread_messages,
            "chat_messages": chat_messages,
            "today": today,
        }
    else:
        context = {
            "user": user,
            "user_list": user_list,
            "unread_messages": unread_messages,
        }
    return render(request, "user_messages.html", context)


def read_message(request, id):
    user = User.objects.get(id=request.session['user_id'])
    other_user = User.objects.get(id=id)
    request.session['other_user'] = other_user.id
    chat_messages = Message.objects.filter(sender=other_user, receiver=user)
    for msg in chat_messages:
        msg.read = True
        msg.save()
    return redirect("/messages")


def close_message(request):
    if 'other_user' in request.session:
        del request.session['other_user']
    return redirect("/messages")


def send_message(request):
    user = User.objects.get(id=request.session['user_id'])
    other_user = User.objects.get(id=request.session['other_user'])
    msg = Message.objects.create(
        body=request.POST['body'], sender=user, receiver=other_user)
    chat_messages = Message.objects.filter(sender=other_user, receiver=user)
    for msg in chat_messages:
        msg.read = True
        msg.save()
    return redirect("/messages")


def user_search(request):
    request.session['user_search'] = request.POST['user_search']
    return redirect('/messages')


def user_remove_search(request):
    del request.session['user_search']
    return redirect('/messages')

# --------------- ADD FRIENDS ----------------- #
# --------------- ADD THEM TO YOUR FRIENDSLIST ----------------- #
def request_friend(request, username):
    user = User.objects.get(id=request.session['user_id'])
    user_to_add = User.objects.get(user_name=username)
    if not user.friends_list:
        friends_list = FriendsList.objects.create(user=user)
    else:
        friends_list = FriendsList.objects.get(user=user)
    friends_list.friends.add(user_to_add)
    friends_list.save()
    return redirect(f'/profile/{username}')

# --------------- THEY ADD YOU BACK ----------------- #
def accept_friend(request, username):
    user = User.objects.get(id=request.session['user_id'])
    user_to_add = User.objects.get(user_name=username)
    if not user.friends_list:
        friends_list = FriendsList.objects.create(user=user)
    else:
        friends_list = FriendsList.objects.get(user=user)
    friends_list.friends.add(user_to_add)
    friends_list.save()
    return redirect('/dash')