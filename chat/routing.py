from django.urls import path
from .consumers import *

websocket_urlpatterns = [
    path("api/ws/chat", ChatConsumer.as_asgi())
]