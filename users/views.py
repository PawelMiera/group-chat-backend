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

                    avatar = pa.PyAvataaar(
                        background_color=random.choice(list(pa.Color)),
                        style=pa.AvatarStyle.TRANSPARENT,
                        skin_color=random.choice(list(pa.SkinColor)),
                        hair_color=random.choice(list(pa.HairColor)),
                        facial_hair_type=random.choice(list(pa.FacialHairType)),
                        facial_hair_color=random.choice(list(pa.HairColor)),
                        top_type=random.choice(list(pa.TopType)),
                        hat_color=random.choice(list(pa.Color)),
                        mouth_type=random.choice(list(pa.MouthType)),
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


class UserView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    def delete(self, request):
        request.user.delete()
        return Response()

    def patch(self, request):
        data = request.data

        request.user.first_name = data.get("first_name", request.user.first_name)
        request.user.extendeduser.avatar = data.get("avatar", request.user.extendeduser.avatar)

        request.user.save()
        request.user.extendeduser.save()
        serializer = UserSerializer(request.user)

        return Response(serializer.data)


class TokenRotateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        refresh = RefreshToken.for_user(request.user)
        return Response({"refresh": str(refresh)})
