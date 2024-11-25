import json

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer

from .models import GroupMessage, ChatGroup
from .utils import get_all_group_ids


class ChatConsumer(WebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.user = None
        self.groups = set()

    def group_update(self, event, type='group_update'):
        self.refresh_groups()
        if str(event["msg"]) in self.groups:
            msg = '{"command": "updateGroup", "groupId": ' + event["msg"] + '}'
            self.send(msg)

    def user_update(self, event, type='user_update'):
        self.refresh_groups()
        if str(event["msg"]) in self.groups:
            msg = '{"command": "updateUser", "groupId": ' + event["msg"] + '}'
            self.send(msg)

    def group_deleted(self, event, type='group_deleted'):
        msg = '{"command": "deleteGroup", "groupId": ' + event["msg"] + '}'
        self.send(msg)
        self.groups.remove(str(event["msg"]))

    def refresh_groups(self):
        group_ids = get_all_group_ids(self.user)
        for group_id in group_ids:
            group_id_str = str(group_id)
            if group_id_str not in self.groups:
                async_to_sync(self.channel_layer.group_add)(
                    group_id_str, self.channel_name
                )
                self.groups.add(group_id_str)

    def connect(self):
        self.user = self.scope["user"]
        if self.user and self.user.is_authenticated:
            group_ids = get_all_group_ids(self.user)
            for group_id in group_ids:
                group_id_str = str(group_id)
                async_to_sync(self.channel_layer.group_add)(
                    group_id_str, self.channel_name
                )
                self.groups.add(group_id_str)
            self.accept()

        else:
            self.close(3000, "Unauthorized")

    def receive(self, text_data=None, bytes_data=None):
        # print("MSG:", text_data)

        try:
            data = json.loads(text_data)
            if data:
                if "command" in data:
                    if data["command"] == "refreshGroups":
                        self.refresh_groups()
                    elif data["command"] == "ping":
                        self.send(text_data='{"command": "pong"}')
                    return

                if "group" in data and data["group"] in self.groups:
                    curr_group = ChatGroup.objects.get(id=data["group"])

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
                        str(data["group"]), event
                    )
        except Exception as e:
            print(e)
            print("WS msg parse error:", text_data)

    def message_handler(self, event):
        self.send(text_data=json.dumps(event["data"]))

    def disconnect(self, code):
        print("Disconnect")
        for group_id in self.groups:
            async_to_sync(self.channel_layer.group_discard)(
                group_id, self.channel_name
            )
        self.groups.clear()
