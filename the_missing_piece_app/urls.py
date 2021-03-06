from django.urls import path
from . import views

urlpatterns = [
    path('', views.index),
    path('guest', views.guest),
    path('register', views.register),
    path('login', views.login),
    path('dash', views.dashboard),
    path('logout', views.logout),
    path('share', views.display_share),
    path('share/create', views.create_share),
    path('share/delete/<int:id>', views.delete),
    path('s_like/<int:id>', views.like_story),
    path('s_unlike/<int:id>', views.unlike_story),
    path('post_comment', views.post_comment),
    path('delete/comment/<int:id>', views.delete_comment),
    path('like/<int:id>', views.like_comment),
    path('unlike/<int:id>', views.unlike_comment),
    path('profile/<username>', views.user_page),
    path('profile/<username>/edit', views.edit_profile),
    path('profile/<username>/add', views.request_friend),
    path('profile/<username>/accept', views.accept_friend),
    path('profile/share/delete/<int:id>', views.delete),
    path('messages/', views.user_messages),
    path('messages/read/<int:id>/', views.read_message),
    path('messages/close/', views.close_message),
    path('messages/send/', views.send_message),
    path('messages/search/', views.user_search),
    path('messages/search/remove/', views.user_remove_search),
]