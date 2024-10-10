from rest_framework import permissions
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import RegisterLoginSerializer, UserSerializer, BasicUserValidator
from django.contrib.auth.models import User
from django.contrib.auth import authenticate

from rest_framework_simplejwt.tokens import RefreshToken
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
                    return Response({'refresh': str(refresh),'access': str(refresh.access_token)}, status=status.HTTP_200_OK)
                else:
                    return Response({"password": "Wrong password"},status=status.HTTP_400_BAD_REQUEST)
            else:
                serializer = RegisterLoginSerializer(data=request.data)

                if serializer and serializer.is_valid():
                    user = serializer.save()
                    refresh = RefreshToken.for_user(user)
                    return Response({'refresh': str(refresh),'access': str(refresh.access_token)},status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(validator.errors, status=status.HTTP_400_BAD_REQUEST)


class UserView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, format=None):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    def delete(self, request, format=None):
        request.user.delete()
        return Response()
