from django.urls import path
from . import views

urlpatterns = [
    path('groups/new/', views.CreateGroupView.as_view(), name='chat_message_view'),
    path('groups/join/', views.JoinGroupView.as_view(), name='chat_message_view'),
    path('groups/all/', views.AllGroupsView.as_view(), name='chat_message_view'),
    path('groups/messages/all', views.AllGroupsMessagesView.as_view(), name='chat_message_view'),
    path('groups/users/all', views.AllGroupsUsersView.as_view(), name='chat_message_view'),

    path('groups/', views.GroupView.as_view(), name='chat_message_view'),
    path('groups/messages/', views.MessageView.as_view(), name='chat_message_view'),
    # path('groups/users/', views.MessageView.as_view(), name='chat_message_view'),

    # path('message/', views.MessageView.as_view(), name='chat_message_view'),
    # path('groups/messages/', views.GroupsMessagesView.as_view(), name='chat_message_view'),
    # path('group/', views.GroupView.as_view(), name='create_group'),
    # path('joinGroup/', views.JoinGroupView.as_view(), name='join_group'),
]
