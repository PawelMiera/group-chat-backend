from channels.generic.websocket import WebsocketConsumer
import json
from .models import GroupMessage, ChatGroup, Membership
from django.shortcuts import get_object_or_404
from asgiref.sync import async_to_sync
from .utils import get_all_groups

class ChatConsumer(WebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.user = None
        self.groups = set()

    def refresh_groups(self):
        groups = get_all_groups(self.user)
        for group in groups:
            group_id_str = str(group.id)
            if group_id_str not in self.groups:
                print("ADDING NEW GROUP", group_id_str)
                async_to_sync(self.channel_layer.group_add)(
                    group_id_str, self.channel_name
                )
                self.groups.add(group_id_str)

    def connect(self):
        self.user = self.scope["user"]
        print("new ws connection")
        if self.user and self.user.is_authenticated:
            groups = get_all_groups(self.user)
            for group in groups:
                group_id_str = str(group.id)
                async_to_sync(self.channel_layer.group_add)(
                    group_id_str, self.channel_name
                )
                self.groups.add(group_id_str)
                print(group_id_str)
            self.accept()

        else:
            self.close(3000, "Unauthorized")

    def receive(self, text_data=None, bytes_data=None):
        print("MSG:", text_data)

        try:
            data = json.loads(text_data)
            if data:
                if "command" in data:
                    if data["command"] == "refreshGroups":
                        self.refresh_groups()
                    elif data["command"] == "ping":
                        self.send(text_data="pong")
                    return

                if "group" in data and data["group"] in self.groups:
                    curr_group = get_object_or_404(ChatGroup, id=data["group"])

                    msg_text = data["msg"]
                    new_msg = GroupMessage.objects.create(
                        group=curr_group,
                        msg=msg_text,
                        author=self.user
                    )

                    data["author"] = self.user.id
                    data["created"] = str(new_msg.created)
                    event = {
                        "type": "message_handler",
                        "data": data
                    }

                    async_to_sync(self.channel_layer.group_send)(
                        data["group"], event
                    )
        except Exception as e:
            print(e)
            print("MSG:", text_data)

    def message_handler(self, event):
        self.send(text_data=json.dumps(event["data"]))

    def disconnect(self, code):
        for group_id in self.groups:
            async_to_sync(self.channel_layer.group_discard)(
                group_id, self.channel_name
            )
        self.groups.clear()
