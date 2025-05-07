from django.shortcuts import render, get_object_or_404
from django.views import View
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from django.db.models import Q
from accounts.models import User
from accounts.serializers import UserSerializer
from chats.serializers import MessageSerializer
from chats.models import Message
from django.db import models

class MessageViewSet(ModelViewSet):
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Message.objects.filter(Q(sender=user) | Q(receiver=user)).order_by('created_at')

    def perform_create(self, serializer):
        serializer.save(sender_id=self.request.user.pk)

    @action(methods=['get'], detail=False)
    def chat_with(self, request):
        other_user_id = request.query_params.get('user_id')

        if not other_user_id:
            return Response({
                "success": False,
                "error": "Please provide a user_id"
            })

        try:
            other_user = User.objects.get(pk=other_user_id)
        except User.DoesNotExist:
            return Response({
                "success": False,
                "error": "Please provide a valid user_id"
            })

        messages = Message.objects.filter(
            Q(sender=request.user) & Q(receiver=other_user),
            Q(sender=other_user) & Q(receiver=request.user)
        )
        serializer = self.get_serializer(messages, many=True)
        return Response(serializer.data)


class ChatRenderView(View):
    def get(self, request):
        return render(request, 'chat.html')


class MessageListView(APIView):
    """
    View to list all messages between the current user and another user.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id=None):
        """
        Return a list of all messages between the request.user and the user with id=user_id.
        """
        other_user = get_object_or_404(User, id=user_id)

        # Get all messages between the two users
        messages = Message.objects.filter(
            (
                # Messages from current user to other user
                    (
                            models.Q(sender=request.user) &
                            models.Q(receiver=other_user)
                    ) |
                    # Messages from other user to current user
                    (
                            models.Q(sender=other_user) &
                            models.Q(receiver=request.user)
                    )
            )
        ).order_by('created_at')

        serializer = MessageSerializer(messages, many=True)
        return Response(serializer.data)


class MarkMessageAsReadView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, message_id=None):
        message = get_object_or_404(Message, id=message_id, receiver=request.user)
        message.is_read = True
        message.save()
        return Response(status=status.HTTP_200_OK)

