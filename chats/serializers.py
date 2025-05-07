from accounts.serializers import UserSerializer
from chats.models import Message
from rest_framework import serializers
from accounts.models import User

class MessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)
    to_user = UserSerializer(read_only=True)
    sender_id = serializers.IntegerField(write_only=True)
    to_user_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Message
        fields = ['id', 'sender', 'to_user', 'sender_id', 'to_user_id', 'content', 'created_at', 'is_read']


    def create(self, validated_data: dict):
        sender_id = validated_data.pop('sender_id')
        to_user_id = validated_data.pop('to_user_id')

        sender_user = User.objects.get(id=sender_id)
        to_user = User.objects.get(id=to_user_id)

        message = Message.objects.create(
            sender=sender_user,
            to_user=to_user,
            **validated_data
        )
        return message

    def validate(self, attrs):
        if str(attrs.get('sender_id')) == str(attrs.get('to_user_id')):
            raise serializers.ValidationError("You can\'t send a message to yourself.")
        return attrs

    # def to_representation(self, instance):
    #     representation = super().to_representation(instance)
    #     # Change 'receiver' to 'to_user_id' for frontend compatibility if needed
    #     # representation['to_user_id'] = representation.pop('receiver')
    #     return representation