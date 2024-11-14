from django import forms
from django.contrib.auth.models import User
from rest_framework import serializers

from .fields import CommaSeparatedField
from .models import ChatGroup, GroupMessage

from identicons import generate
import colorsys
import cv2
import base64
import random
import numpy as np

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


class CreateGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatGroup
        fields = ('uuid', 'name')

    def create(self, validated_data):

        available_colors = [
            0x4d9eff, #orange
            0xff634c, #blue
            0xff4ca7, #purple
            0xffce4c, #lightblue
            0x221a8e, #red
            0x145712, #green
            0x0f3264, #brown
            0x5d27ea #pink
        ]
        icon_custom = generate(validated_data['name'] + str(random.uniform(0, 1)), primary=0xFFFFFF,
                               secondary=random.choice(available_colors))

        i, j = icon_custom.shape[:2]
        h, w = 250 // i, 250 // j
        large_identicon = np.repeat(icon_custom, h, axis=0)
        large_identicon = np.repeat(large_identicon, w, axis=1)

        retval, buffer_img = cv2.imencode('.jpg', large_identicon)
        img_data = base64.b64encode(buffer_img)
        img_str = img_data.decode("utf-8")

        group = ChatGroup.objects.create(
            name=validated_data['name'],
            avatar="data:image/jpeg;base64," + img_str
        )
        return group


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatGroup
        fields = ('uuid', 'name')

    def create(self, validated_data):

        group = ChatGroup.objects.create(
            name=validated_data['name'],
        )
        return group


class GetMessageValidator(forms.Form):
    start = forms.IntegerField()
    end = forms.IntegerField()

class PostMessageValidator(forms.Form):
    msg = forms.CharField()
    group_uuid = forms.CharField()


class GetGroupsMessagesValidator(forms.Form):
    groups = CommaSeparatedField(label='Input names (separate with commas): ')
    start = forms.IntegerField()
    end = forms.IntegerField()


class AllGroupsMessagesValidator(forms.Form):
    start = forms.IntegerField()
    end = forms.IntegerField()


class GroupValidator(forms.Form):
    uuid = forms.CharField()


class GetMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = GroupMessage
        fields = ['msg', 'author', 'created']


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", 'first_name', 'username', "date_joined"]
