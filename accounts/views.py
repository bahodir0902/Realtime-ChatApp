from django.shortcuts import render, get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from accounts.models import User
from accounts.serializers import UserSerializer, RegisterUserSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from chats.serializers import MessageSerializer
from chats.models import Message
from django.db import models

class SessionView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)


class RegisterUserView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterUserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        user_serializer = UserSerializer(user)

        refresh = RefreshToken.for_user(user)

        return Response({
            'user': user_serializer.data,
            'refresh': str(refresh),
            "access": str(refresh.access_token),
        })

class ContactsAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        users = User.objects.all().exclude(id=request.user.pk)
        serializers = UserSerializer(users, many=True)
        return Response(serializers.data)

