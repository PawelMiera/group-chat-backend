from .serializers import *
from .models import *


def get_messages(group, start, end):
    start = int(start)
    end = int(end)
    end = max(start, end)
    start = min(start, end)

    messages = GroupMessage.objects.filter(group=group)
    start = min(start, len(messages))
    end = min(end, len(messages))
    serialized_messages = GetMessageSerializer(reversed(messages[start: end]), many=True)
    return serialized_messages.data


def get_all_messages(user, start, end):
    groups = Membership.objects.filter(user=user).values_list("group", flat=True)
    groups_data = ChatGroup.objects.filter(id__in=groups)
    all_messages = {}
    for group in groups_data:
        all_messages[group.uuid] = get_messages(group, start, end)
    return all_messages


def get_users(groups):
    members = Membership.objects.filter(group__in=groups).values_list('user', flat=True).distinct()
    users = User.objects.filter(id__in=members)
    out_users = []
    for user in users:
        name = user.first_name if (user.first_name and user.first_name != "") else user.username
        out_users.append(
            {"name": name, "date_joined": user.date_joined, "id": user.id, "avatar": user.extendeduser.avatar})
    return out_users


def get_all(user, start, end):
    groups = Membership.objects.filter(user=user).values_list("group", flat=True)
    groups_data = ChatGroup.objects.filter(id__in=groups)
    out_messages = []
    out_groups = []
    out_users = get_users(groups)
    for group in groups_data:
        messages = get_messages(group, start, end)
        # last_msg = {"msg": "", "author": "", "created": ""}
        # if len(messages) > 0:
        #     last_msg = messages[-1]
        curr_group_member_ids = list(Membership.objects.filter(group=group).values_list('user', flat=True))
        out_group = {"id": group.id, "name": group.name, "uuid": group.uuid, "members": curr_group_member_ids,
                     "last_activity": messages[-1]["created"], "avatar": group.avatar} #"last_msg": last_msg,
        out_groups.append(out_group)
        out_messages.append({"group_id": group.id, "messages": messages})

    curr_user = {"username": user.username, "date_joined": user.date_joined, "id": user.id, "nickname": user.first_name,
                 "avatar": user.extendeduser.avatar, "anonymous": user.extendeduser.anonymous}

    server_user = User.objects.get(username="server")

    return {"groups": out_groups, "users": out_users, "messages": out_messages, "curr_user": curr_user,
            "server_id": server_user.id}


def get_single_group(group, start=0, end=25):
    messages = get_messages(group, start, end)
    # last_msg = {"msg": "", "author": "", "created": ""}
    # if len(messages) > 0:
    #     last_msg = messages[-1]
    curr_group_member_ids = list(Membership.objects.filter(group=group).values_list('user', flat=True))
    out_users = get_users([group])

    return {"group": {"id": group.id, "name": group.name, "uuid": group.uuid, "members": curr_group_member_ids,
            "last_activity": messages[-1]["created"], "avatar": group.avatar}, "messages": messages, "users": out_users} #"last_msg": last_msg,


def get_all_groups_raw(user):
    groups = Membership.objects.filter(user=user).values_list("group", flat=True)
    groups_data = ChatGroup.objects.filter(id__in=groups)
    return groups_data

def get_all_group_ids(user):
    group_ids = Membership.objects.filter(user=user).values_list("group", flat=True)
    return list(group_ids)

def get_group_user_ids(group):
    user_ids = Membership.objects.filter(group=group).values_list("user", flat=True)
    return list(user_ids)
