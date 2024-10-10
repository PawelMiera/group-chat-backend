from django.urls import path
from . import views

urlpatterns = [
    path('message/', views.MessageView.as_view(), name='chat_message_view'),
    path('group/', views.GroupView.as_view(), name='create_group'),
    path('joinGroup/', views.JoinGroupView.as_view(), name='join_group'),
]
