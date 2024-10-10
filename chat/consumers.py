from channels.generic.websocket import WebsocketConsumer
import json
from .models import GroupMessage, ChatGroup, Membership
from django.shortcuts import get_object_or_404
from asgiref.sync import async_to_sync


class ChatConsumer(WebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.user = None
        self.groups = set()

    def refresh_groups(self):
        member_groups = Membership.objects.get(user=self.user)
        for member_group in member_groups:
            group_id = member_group.group.group_id
            if group_id not in self.groups:
                print("ADDING NEW GROUP", member_group.group.group_id)
                async_to_sync(self.channel_layer.group_add)(
                    group_id, self.channel_name
                )
                self.groups.add(member_group.group.group_id)

    def connect(self):
        self.user = self.scope["user"]
        if self.user and self.user.is_authenticated:

            member_groups = Membership.objects.get(user=self.user)
            for member_group in member_groups:
                async_to_sync(self.channel_layer.group_add)(
                    member_group.group.group_id, self.channel_name
                )
                self.groups.add(member_group.group.group_id)
                print(member_group.group.group_id)
            self.accept()

        else:
            self.close(3000, "Unauthorized")

    def receive(self, text_data=None, bytes_data=None):
        data = json.loads(text_data)
        if data:
            if "refreshGroups" in data and data["refreshGroups"]:
                self.refresh_groups()

            if data["group"] in self.groups:
                chatroom = get_object_or_404(ChatGroup, group_id=data["group"])
                msg_text = data["msg"]
                GroupMessage.objects.create(
                    group=chatroom,
                    msg=msg_text,
                    author=self.user
                )

                data["user"] = self.user.username

                event = {
                    "type": "message_handler",
                    "data": data
                }

                async_to_sync(self.channel_layer.group_send)(
                    data["group"], event
                )
            else:
                print(self.user + " not in " + data["group"])

    def message_handler(self, event):
        self.send(text_data=json.dumps(event["data"]))

    def disconnect(self, code):
        for group_id in self.groups:
            async_to_sync(self.channel_layer.group_discard)(
                group_id, self.channel_name
            )
        self.groups.clear()
