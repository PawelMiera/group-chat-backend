from rest_framework import serializers
from .models import ChatGroup, Membership, GroupMessage
from django import forms
from django.contrib.auth.models import User


class GroupMessageSerializer(serializers.ModelSerializer):
    def __init__(self, user, **kwargs, ):
        super().__init__(**kwargs)
        self.user = user

    class Meta:
        model = GroupMessage
        fields = ['group', 'msg']

    def create(self, validated_data):
        group = GroupMessage.objects.create(
            group=validated_data['group'],
            msg=validated_data['msg'],
            author=self.user
        )
        return group


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatGroup
        fields = ('group_id', 'group_name')

    def create(self, validated_data):
        group = ChatGroup.objects.create(
            group_name=validated_data['group_name'],
        )
        return group


class AllGroupsSerializer:
    @staticmethod
    def serialize(user: User):
        groups = []
        curr_member_group_ids = Membership.objects.filter(user=user).values_list("group")
        curr_member_groups = ChatGroup.objects.filter(pk__in=curr_member_group_ids)

        for curr_member_group in curr_member_groups:
            curr_group_member_ids = Membership.objects.filter(group=curr_member_group).values_list('user', flat=True)
            curr_group_members = User.objects.filter(pk__in=curr_group_member_ids)
            members = []
            for member_data in curr_group_members:
                members.append({"username": member_data.username,
                                "nick": member_data.first_name})  # , "joined": member_data.date_joined
            group = {"name": curr_member_group.group_name, "id": curr_member_group.group_id, "members": members}
            groups.append(group)
        return {"groups": groups}


class BasicGroupvalidator(forms.Form):
    group_id = forms.CharField(max_length=100)


class GetMessageValidator(forms.Form):
    group = forms.CharField(max_length=100)
    start = forms.IntegerField()
    end = forms.IntegerField()


class GetMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = GroupMessage
        fields = ['msg', 'author', 'created']


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name', 'username', "date_joined"]
