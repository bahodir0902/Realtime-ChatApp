from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from accounts.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'email']

class RegisterUserSerializer(serializers.ModelSerializer):
    re_password = serializers.CharField(max_length=255)
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'password', 're_password']


    def create(self, validated_data):

        user = User.objects.create_user(
            **validated_data
        )

        return user

    def validate(self, attrs):
        re_password = attrs.pop('re_password')
        password = attrs.get('password')

        if str(re_password) != str(password):
            raise ValidationError("Passwords don\'t match.")

        email = attrs.get("email")
        if User.objects.filter(email=email).exists():
            raise ValidationError("User with this email already exists.")

        return attrs