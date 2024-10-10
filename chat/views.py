from django.shortcuts import get_object_or_404
from rest_framework import permissions
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import *
from .utils import get_messages

class MessageView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = GroupMessageSerializer(data=request.data, user=request.user)
        if serializer.is_valid():
            member_exists = Membership.objects.filter(user=request.user, group=serializer.validated_data["group"]).exists()
            if member_exists:
                serializer.save()
                return Response()
            return Response({"error": "Not a member of the group"}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        validator = GetMessageValidator(data=request.data)
        if validator.is_valid():
            messages = get_messages(validator.data["group"], validator.data["start"], validator.data["end"])

            return Response({"messages": messages, "len": len(messages)})
        return Response(validator.errors, status=status.HTTP_400_BAD_REQUEST)


class GroupView(APIView):
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

    def delete(self, request):
        validator = BasicGroupvalidator(request.data)
        if validator.is_valid():
            curr_group = get_object_or_404(ChatGroup, group_id=validator.data["group_id"])
            curr_group.delete()
            return Response()
        return Response(validator.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        return Response(AllGroupsSerializer.serialize(request.user))


class JoinGroupView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        validator = BasicGroupvalidator(request.POST)

        if validator.is_valid():
            curr_group = get_object_or_404(ChatGroup, group_id=validator.data["group_id"])

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

        return Response(validator.errors, status=status.HTTP_400_BAD_REQUEST)
