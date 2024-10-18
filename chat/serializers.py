from rest_framework import serializers
from .models import ChatGroup, Membership, GroupMessage
from django import forms
from django.contrib.auth.models import User
from .fields import CommaSeparatedField


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


class GetMessageValidator(forms.Form):
    start = forms.IntegerField()
    end = forms.IntegerField()

class PostMessageValidator(forms.Form):
    msg = forms.CharField()
    group_id = forms.CharField()


class GetGroupsMessagesValidator(forms.Form):
    groups = CommaSeparatedField(label='Input names (separate with commas): ')
    start = forms.IntegerField()
    end = forms.IntegerField()


class AllGroupsMessagesValidator(forms.Form):
    start = forms.IntegerField()
    end = forms.IntegerField()


class GroupValidator(forms.Form):
    group_id = forms.CharField()


class GetMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = GroupMessage
        fields = ['msg', 'author', 'created']


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", 'first_name', 'username', "date_joined"]
