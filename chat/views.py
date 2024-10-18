from django.shortcuts import get_object_or_404
from rest_framework import permissions
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .utils import *
from .serializers import *

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


class AllGroupsUsersView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
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
        serializer = GroupSerializer(data=request.data)
        if serializer.is_valid():
            curr_group = serializer.save()

            Membership.objects.create(
                user=request.user,
                group=curr_group,
                admin=True
            )

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
            curr_group = get_object_or_404(ChatGroup, group_id=validator.cleaned_data["group_id"])
            member_exists = Membership.objects.filter(user=request.user, group=curr_group).exists()
            if member_exists:
                GroupMessage.objects.create(group=curr_group, author=request.user, msg=validator.cleaned_data["msg"])
                return Response()
            return Response({"error": "Not a member of the group"}, status=status.HTTP_400_BAD_REQUEST)
        return Response(validator.errors, status=status.HTTP_400_BAD_REQUEST)

#
#     def get(self, request, group_id):
#         if group_id and group_id != "":
#
#             validator = GetMessageValidator(data=request.GET)
#             if validator.is_valid():
#                 messages = get_messages(validator.cleaned_data["group"], validator.cleaned_data["start"],
#                                         validator.cleaned_data["end"])
#
#                 return Response({"messages": messages, "len": len(messages)})
#             return Response(validator.errors, status=status.HTTP_400_BAD_REQUEST)
#         return Response({"error": "group_id is missing"}, status=status.HTTP_400_BAD_REQUEST)


class GroupView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request):
        validator = GroupValidator(data=request.data)
        if validator.is_valid():
            curr_group = get_object_or_404(ChatGroup, group_id=validator.cleaned_data["group_id"])

            member = Membership.objects.get(user=request.user, group=curr_group)
            if member.admin:
                curr_group.delete()
                return Response()
            else:
                Response({"error": "User is not admin"}, status=status.HTTP_400_BAD_REQUEST)
        return Response(validator.errors, status=status.HTTP_400_BAD_REQUEST)


class JoinGroupView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, group_id):
        if group_id and group_id != "":
            curr_group = get_object_or_404(ChatGroup, group_id=group_id)

            member_exists = Membership.objects.filter(user=request.user, group=curr_group).exists()

            if not member_exists:
                Membership.objects.create(
                    user=request.user,
                    group=curr_group,
                    admin=False
                )

                return Response(GroupSerializer(curr_group).data, status=status.HTTP_201_CREATED)
            else:
                return Response({"error": "Already a member"}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"error": "group_id is missing"}, status=status.HTTP_400_BAD_REQUEST)
