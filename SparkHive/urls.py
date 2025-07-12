from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup, name='signup'),
    path('logout/', views.logout_view, name='logout'),
    path('like/<int:idea_id>/', views.like_idea, name='like'),
    path('comment/<int:idea_id>/', views.comment_on_idea, name='comment'),
    path('follow/<int:user_id>/', views.follow_unfollow, name='follow'),
    path('profile/', views.profile, name='profile'),
    path('search/', views.search_community, name='search'),
    path('chat/', views.chat_system, name='chat'),
    path('chat/<int:user_id>/', views.chat_system, name='chat_user'),
    path('notifications/', views.notifications_view, name='notifications'),
    path('idea/edit/<int:idea_id>/', views.edit_idea, name='edit_idea'),
    path('idea/delete/<int:idea_id>/', views.delete_idea, name='delete_idea'),
]
