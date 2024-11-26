from django.urls import path
from .consumers import *

websocket_urlpatterns = [
    path("groopieWs/", ChatConsumer.as_asgi())
]