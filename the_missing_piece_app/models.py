from django.db import models
from datetime import datetime
import re

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]+$')

class UserManager(models.Manager):
    def validator(self, data):
        get_email = User.objects.filter(email=data['email'])
        get_username = User.objects.filter(user_name=data['user_name'])
        errors = {}
        if len(data['user_name']) < 1:
            errors['user_name'] = "Username cannot be empty"
        if len(get_username) > 0:
            errors["user_exists"] = "Username already taken"
        if len(data['first_name']) < 2:
            errors['first_name'] = "First Name has to be at least 2 characters"
        if len(data['last_name']) < 2:
            errors['last_name'] = "Last Name has to be at least 1 character"
        if len(get_email) > 0:
            errors["email_exists"] = "Email already exists"
        if not EMAIL_REGEX.match(data['email']):
            errors['email'] = "Email is invalid"
        if data['birthday'] == '':
            errors['birthday'] = "Date cannot be empty"
        else: 
            if datetime.strptime(data['birthday'], '%Y-%m-%d') > datetime.today():
                errors['birthday'] = "Date cannot be in the future"
        if data['password'] != data['cpassword']:
            errors['password'] = "Passwords do not match"
        if len(data['password']) < 8:
            errors['password'] = "Password is too short"
        return errors

    def login_validator(self, data):
        get_email = User.objects.filter(email=data['email'])
        login_errors = {}
        if len(data['email']) == 0:
            login_errors['email_empty'] = "Enter a valid email"
        if (len(get_email) == 0):
            login_errors["email_does_not_exist"] = "Email does not exist."    
        if not EMAIL_REGEX.match(data['email']):
            login_errors['email1'] = "Email is invalid"
        if len(data['password']) < 8:
            login_errors['password'] = "Password is too short"
        return login_errors

class StoryManager(models.Manager):
    def validator(self, data):
        errors={}
        if len(data['who']) < 2:
            errors["who"] = "Name must contain at least 2 characters!"
        if data['desc'] == "":
            errors["desc"] = "A description must be provided!"
        return errors

class CommentManager(models.Manager):
    def validator(self, data):
        errors={}
        if len(data['comment']) < 1:
            errors["comment"] = "Comment cannot be empty"
        return errors

class User(models.Model):
    profile_pic = models.ImageField(upload_to='profile_pics/', default='profile_pics/None/no-img.jpg')
    logged_in = models.BooleanField(default=False)
    user_name = models.CharField(max_length=60)
    first_name = models.CharField(max_length=60)
    last_name = models.CharField(max_length=60)
    birthday = models.DateTimeField()
    email = models.CharField(max_length=60)
    password = models.CharField(max_length=60)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = UserManager()

    def __str__(self):
        return self.first_name + " " + self.last_name

class FriendsList(models.Model):
    user = models.ForeignKey(User, related_name="friends_list", on_delete = models.CASCADE)
    friends = models.ManyToManyField(User, related_name="friends")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Story(models.Model):
    who = models.CharField(max_length=60)
    desc = models.TextField()
    story_img = models.ImageField(upload_to='images/')
    submitted_by = models.ForeignKey(User, related_name="user_story", on_delete = models.CASCADE)
    user_likes = models.ManyToManyField(User, related_name="story_liked")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = StoryManager()

    def __str__(self):
        return self.submitted_by.first_name + " " + self.submitted_by.last_name + " " + self.who 

class Comment(models.Model):
    user = models.ForeignKey(User, related_name="comments", on_delete = models.CASCADE)
    comment = models.TextField()
    commented_story = models.ForeignKey(Story, related_name="story_comments", on_delete = models.CASCADE)
    c_user_likes = models.ManyToManyField(User, related_name="comment_liked")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = CommentManager()

    def __str__(self):
        return self.user.first_name + " " + self.user.last_name + ":" + self.commented_story.who 

class Message(models.Model):
    body = models.TextField()
    read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    sender = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name='sender')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name='receiver')
    #receiver = models.ManyToManyField(User, related_name='receiver')
    
    def __str__(self):
        return str(self.created_at)
