from django.shortcuts import get_object_or_404
from rest_framework import permissions
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .utils import *
from .serializers import *

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


class AllGroupsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        validator = AllGroupsMessagesValidator(data=request.GET)
        if validator.is_valid():
            start = validator.cleaned_data["start"]
            end = validator.cleaned_data["end"]
            ret = get_all(request.user, start, end)

            return Response(ret)
        return Response(validator.errors, status=status.HTTP_400_BAD_REQUEST)


class AllGroupUsersView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        curr_member_group_ids = Membership.objects.filter(user=request.user).values_list("group", flat=True)
        ret = get_users(curr_member_group_ids)
        return Response(ret)


class GroupUsersView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        validator = GroupValidator(data=request.GET)
        if validator.is_valid():
            curr_group = get_object_or_404(ChatGroup, uuid=validator.cleaned_data["uuid"])

            member_exists = Membership.objects.filter(user=request.user, group=curr_group).exists()

            if member_exists:
                ret = get_users([curr_group.id])
                return Response(ret)
            else:
                return Response({"error": "User is not a member"}, status=status.HTTP_400_BAD_REQUEST)

        return Response(validator.errors, status=status.HTTP_400_BAD_REQUEST)

        curr_member_group_ids = Membership.objects.filter(user=request.user).values_list("group", flat=True)
        ret = get_users(curr_member_group_ids)
        return Response(ret)


class AllGroupsMessagesView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        validator = AllGroupsMessagesValidator(data=request.GET)
        if validator.is_valid():
            start = validator.cleaned_data["start"]
            end = validator.cleaned_data["end"]
            ret = get_all_messages(request.user, start, end)

            return Response(ret)
        return Response(validator.errors, status=status.HTTP_400_BAD_REQUEST)


class CreateGroupView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = CreateGroupSerializer(data=request.data)
        if serializer.is_valid():
            curr_group = serializer.save()

            Membership.objects.create(
                user=request.user,
                group=curr_group,
                admin=True
            )
            server_user = get_object_or_404(User, username="server")
            GroupMessage.objects.create(group=curr_group, msg="Beginning of the conversation", author=server_user)

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GroupsMessagesView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        validator = GetGroupsMessagesValidator(data=request.data)
        if validator.is_valid():
            start = validator.cleaned_data["start"]
            end = validator.cleaned_data["end"]
            groups = set(validator.cleaned_data["groups"])
            ret = {group: get_messages(group, start, end) for group in groups}

            return Response(ret)
        return Response(validator.errors, status=status.HTTP_400_BAD_REQUEST)


class MessageView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        validator = PostMessageValidator(data=request.data)
        if validator.is_valid():
            curr_group = get_object_or_404(ChatGroup, uuid=validator.cleaned_data["group_uuid"])
            member_exists = Membership.objects.filter(user=request.user, group=curr_group).exists()
            if member_exists:
                GroupMessage.objects.create(group=curr_group, author=request.user, msg=validator.cleaned_data["msg"])
                return Response()
            return Response({"error": "Not a member of the group"}, status=status.HTTP_400_BAD_REQUEST)
        return Response(validator.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        validator = GetMessageValidator(data=request.GET)
        if validator.is_valid():
            curr_group = get_object_or_404(ChatGroup, uuid=validator.cleaned_data["groupUuid"])
            member_exists = Membership.objects.filter(user=request.user, group=curr_group).exists()

            if member_exists:
                messages = get_messages(curr_group, validator.cleaned_data["start"], validator.cleaned_data["end"])
                return Response({"messages": messages})
            return Response({"error": "Not a member of the group"}, status=status.HTTP_400_BAD_REQUEST)

        return Response(validator.errors, status=status.HTTP_400_BAD_REQUEST)


class GroupView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request):
        validator = GroupValidator(data=request.GET)
        if validator.is_valid():
            curr_group = get_object_or_404(ChatGroup, uuid=validator.cleaned_data["uuid"])

            member_exists = Membership.objects.filter(user=request.user, group=curr_group).exists()

            if member_exists:
                channel_layer = get_channel_layer()

                async_to_sync(channel_layer.group_send)(
                    str(curr_group.id),
                    {
                        'type': 'group_deleted',
                        'msg': str(curr_group.id)
                    }
                )

                curr_group.delete()
                return Response()
            else:
                return Response({"error": "User is not a member"}, status=status.HTTP_400_BAD_REQUEST)
        return Response(validator.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        validator = GroupWithMessagesValidator(data=request.GET)
        if validator.is_valid():
            curr_group = get_object_or_404(ChatGroup, uuid=validator.cleaned_data["uuid"])

            member_exists = Membership.objects.filter(user=request.user, group=curr_group).exists()

            if member_exists:
                ret = get_single_group(curr_group, validator.cleaned_data["start"], validator.cleaned_data["end"])
                return Response(ret)
            else:
                return Response({"error": "User is not a member"}, status=status.HTTP_400_BAD_REQUEST)

        return Response(validator.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request):
        validator = GroupValidator(data=request.data)
        if validator.is_valid():
            curr_group = get_object_or_404(ChatGroup, uuid=validator.cleaned_data["uuid"])

            member_exists = Membership.objects.filter(user=request.user, group=curr_group).exists()

            if member_exists:
                data = request.data

                curr_group.name = data.get("name", curr_group.name)
                curr_group.avatar = data.get("avatar", curr_group.avatar)

                curr_group.save()
                serializer = GroupSerializer(curr_group)

                channel_layer = get_channel_layer()

                async_to_sync(channel_layer.group_send)(
                    str(curr_group.id),
                    {
                        'type': 'group_update',
                        'msg': str(curr_group.id)
                    }
                )

                return Response(serializer.data)
            else:
                return Response({"error": "User is not a member"}, status=status.HTTP_400_BAD_REQUEST)
        return Response(validator.errors, status=status.HTTP_400_BAD_REQUEST)


class JoinGroupView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        validator = GroupValidator(data=request.data)
        if validator.is_valid():
            curr_group = get_object_or_404(ChatGroup, uuid=validator.cleaned_data["uuid"])

            member_exists = Membership.objects.filter(user=request.user, group=curr_group).exists()

            if not member_exists:
                Membership.objects.create(
                    user=request.user,
                    group=curr_group,
                    admin=False
                )

                channel_layer = get_channel_layer()

                async_to_sync(channel_layer.group_send)(
                    str(curr_group.id),
                    {
                        'type': 'group_update',
                        'msg': str(curr_group.id)
                    }
                )

                return Response(GroupSerializer(curr_group).data)
            else:
                return Response({"error": "Already a member"}, status=status.HTTP_400_BAD_REQUEST)

        return Response(validator.errors, status=status.HTTP_400_BAD_REQUEST)


class LeaveGroupView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        validator = GroupValidator(data=request.data)
        if validator.is_valid():
            curr_group = get_object_or_404(ChatGroup, uuid=validator.cleaned_data["uuid"])

            membership = get_object_or_404(Membership, group=curr_group, user=request.user)

            if len(get_group_user_ids(curr_group)) > 1:
                membership.delete()

                GroupMessage.objects.filter(author=request.user).delete()

                channel_layer = get_channel_layer()

                async_to_sync(channel_layer.group_send)(
                    str(curr_group.id),
                    {
                        'type': 'group_update',
                        'msg': str(curr_group.id)
                    }
                )

            else:
                membership.delete()
                curr_group.delete()

            return Response()

        return Response(validator.errors, status=status.HTTP_400_BAD_REQUEST)
