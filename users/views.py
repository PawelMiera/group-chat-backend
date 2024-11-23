from rest_framework import permissions
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import RegisterLoginSerializer, UserSerializer, BasicUserValidator
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from .models import ExtendedUser

from rest_framework_simplejwt.tokens import RefreshToken
import py_avataaars as pa
import io
import cv2
import numpy as np
import base64
import random
from chat.utils import get_all_group_ids

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

import datetime
import shortuuid
from names_generator import generate_name

class RegisterLoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, format=None):
        validator = BasicUserValidator(request.data)
        if validator.is_valid():
            user_exists = User.objects.filter(username=validator.data['username']).exists()

            if user_exists:
                user = authenticate(request, username=validator.data["username"], password=validator.data["password"])
                if user is not None:
                    refresh = RefreshToken.for_user(user)
                    return Response({'refresh': str(refresh), 'access': str(refresh.access_token)},
                                    status=status.HTTP_200_OK)
                else:
                    return Response({"password": "Wrong password"}, status=status.HTTP_400_BAD_REQUEST)
            else:
                serializer = RegisterLoginSerializer(data=request.data)

                if serializer and serializer.is_valid():
                    user = serializer.save()
                    avatar_bytes = io.BytesIO()

                    hair_color = random.choice(list(pa.HairColor))

                    top_type = random.choice(list(pa.TopType))

                    no_facial = [pa.TopType.HIJAB, pa.TopType.LONG_HAIR_BIG_HAIR, pa.TopType.LONG_HAIR_BOB,
                                 pa.TopType.LONG_HAIR_BUN,
                                 pa.TopType.LONG_HAIR_CURLY, pa.TopType.LONG_HAIR_CURVY, pa.TopType.LONG_HAIR_DREADS,
                                 pa.TopType.LONG_HAIR_FRIDA,
                                 pa.TopType.LONG_HAIR_FRO_BAND, pa.TopType.LONG_HAIR_NOT_TOO_LONG,
                                 pa.TopType.LONG_HAIR_MIA_WALLACE,
                                 pa.TopType.LONG_HAIR_SHAVED_SIDES, pa.TopType.LONG_HAIR_STRAIGHT,
                                 pa.TopType.LONG_HAIR_STRAIGHT2,
                                 pa.TopType.LONG_HAIR_STRAIGHT_STRAND, pa.TopType.LONG_HAIR_SHAVED_SIDES]

                    facial_type = random.choice(list(pa.FacialHairType))

                    if top_type in no_facial:
                        facial_type = pa.FacialHairType.DEFAULT

                    reduced_mouth_type = list(pa.MouthType)
                    reduced_mouth_type.remove(pa.MouthType.VOMIT)
                    reduced_mouth_type.remove(pa.MouthType.TONGUE)

                    avatar = pa.PyAvataaar(
                        background_color=random.choice(list(pa.Color)),
                        style=pa.AvatarStyle.TRANSPARENT,
                        skin_color=random.choice(list(pa.SkinColor)),
                        hair_color=hair_color,
                        facial_hair_type=facial_type,
                        facial_hair_color=hair_color,
                        top_type=top_type,
                        hat_color=random.choice(list(pa.Color)),
                        mouth_type=random.choice(reduced_mouth_type),
                        eye_type=random.choice(list(pa.EyesType)),
                        eyebrow_type=random.choice(list(pa.EyebrowType)),
                        nose_type=random.choice(list(pa.NoseType)),
                        accessories_type=random.choice(list(pa.AccessoriesType)),
                        clothe_type=random.choice(list(pa.ClotheType)),
                        clothe_color=random.choice(list(pa.Color)),
                        clothe_graphic_type=random.choice(list(pa.ClotheGraphicType))
                    )

                    avatar.render_png_file(avatar_bytes)

                    img = cv2.imdecode(np.frombuffer(avatar_bytes.getbuffer(), np.uint8), 1)
                    img = cv2.resize(img, (250, 250))
                    retval, buffer_img = cv2.imencode('.jpg', img)
                    img_data = base64.b64encode(buffer_img)
                    img_str = img_data.decode("utf-8")

                    ExtendedUser(user=user, avatar="data:image/jpeg;base64," + img_str).save()
                    refresh = RefreshToken.for_user(user)
                    return Response({'refresh': str(refresh), 'access': str(refresh.access_token)},
                                    status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(validator.errors, status=status.HTTP_400_BAD_REQUEST)


class RegisterAnonymousView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, format=None):
        nickname = generate_name(style='capital') + " Anonymous"
        user = User.objects.create(
            username=shortuuid.uuid(),
            first_name=nickname,
            last_login=datetime.datetime.now(),
            password="anonymous"
        )

        user.save()
        avatar_bytes = io.BytesIO()

        hair_color = random.choice(list(pa.HairColor))

        top_type = random.choice(list(pa.TopType))

        no_facial = [pa.TopType.HIJAB, pa.TopType.LONG_HAIR_BIG_HAIR, pa.TopType.LONG_HAIR_BOB,
                     pa.TopType.LONG_HAIR_BUN,
                     pa.TopType.LONG_HAIR_CURLY, pa.TopType.LONG_HAIR_CURVY, pa.TopType.LONG_HAIR_DREADS,
                     pa.TopType.LONG_HAIR_FRIDA,
                     pa.TopType.LONG_HAIR_FRO_BAND, pa.TopType.LONG_HAIR_NOT_TOO_LONG,
                     pa.TopType.LONG_HAIR_MIA_WALLACE,
                     pa.TopType.LONG_HAIR_SHAVED_SIDES, pa.TopType.LONG_HAIR_STRAIGHT,
                     pa.TopType.LONG_HAIR_STRAIGHT2,
                     pa.TopType.LONG_HAIR_STRAIGHT_STRAND, pa.TopType.LONG_HAIR_SHAVED_SIDES]

        facial_type = random.choice(list(pa.FacialHairType))

        if top_type in no_facial:
            facial_type = pa.FacialHairType.DEFAULT

        reduced_mouth_type = list(pa.MouthType)
        reduced_mouth_type.remove(pa.MouthType.VOMIT)
        reduced_mouth_type.remove(pa.MouthType.TONGUE)

        avatar = pa.PyAvataaar(
            background_color=random.choice(list(pa.Color)),
            style=pa.AvatarStyle.TRANSPARENT,
            skin_color=random.choice(list(pa.SkinColor)),
            hair_color=hair_color,
            facial_hair_type=facial_type,
            facial_hair_color=hair_color,
            top_type=top_type,
            hat_color=random.choice(list(pa.Color)),
            mouth_type=random.choice(reduced_mouth_type),
            eye_type=random.choice(list(pa.EyesType)),
            eyebrow_type=random.choice(list(pa.EyebrowType)),
            nose_type=random.choice(list(pa.NoseType)),
            accessories_type=random.choice(list(pa.AccessoriesType)),
            clothe_type=random.choice(list(pa.ClotheType)),
            clothe_color=random.choice(list(pa.Color)),
            clothe_graphic_type=random.choice(list(pa.ClotheGraphicType))
        )

        avatar.render_png_file(avatar_bytes)

        img = cv2.imdecode(np.frombuffer(avatar_bytes.getbuffer(), np.uint8), 1)
        img = cv2.resize(img, (250, 250))
        img = cv2.circle(img, (125, 210), 40, (0, 0, 110), -1)
        img = cv2.putText(img=img, text="A", org=(100, 235), fontFace=cv2.FONT_HERSHEY_DUPLEX, fontScale=2.5,
                          color=(240, 240, 240), thickness=8)
        retval, buffer_img = cv2.imencode('.jpg', img)
        img_data = base64.b64encode(buffer_img)
        img_str = img_data.decode("utf-8")

        ExtendedUser(user=user, anonymous=True, avatar="data:image/jpeg;base64," + img_str).save()
        refresh = RefreshToken.for_user(user)
        return Response({'refresh': str(refresh), 'access': str(refresh.access_token)},
                        status=status.HTTP_200_OK)


class UserView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    def delete(self, request):
        all_ids = get_all_group_ids(request.user)
        channel_layer = get_channel_layer()

        for curr_id in all_ids:
            async_to_sync(channel_layer.group_send)(
                str(curr_id),
                {
                    'type': 'group_update',
                    'msg': str(curr_id)
                }
            )
        request.user.delete()

        return Response()

    def patch(self, request):
        data = request.data

        request.user.first_name = data.get("first_name", request.user.first_name)
        request.user.extendeduser.avatar = data.get("avatar", request.user.extendeduser.avatar)

        request.user.save(update_fields=["first_name"])
        request.user.extendeduser.save(update_fields=["avatar"])
        serializer = UserSerializer(request.user)

        all_ids = get_all_group_ids(request.user)
        channel_layer = get_channel_layer()

        for curr_id in all_ids:
            async_to_sync(channel_layer.group_send)(
                str(curr_id),
                {
                    'type': 'user_update',
                    'msg': str(curr_id)
                }
            )

        return Response(serializer.data)


class TokenRotateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        refresh = RefreshToken.for_user(request.user)
        return Response({"refresh": str(refresh)})


class CheckInView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        request.user.last_login = datetime.datetime.now()
        request.user.save(update_fields=["last_login"])
        return Response()
