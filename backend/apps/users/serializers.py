from rest_framework import serializers
from django.contrib.auth import authenticate
from zoneinfo import available_timezones
from django.contrib.auth import get_user_model
from .models import EmailVerificationToken

User = get_user_model()

ALL_TIMEZONES = sorted(available_timezones())


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "email",
            "role",
            "timezone",
            "email_verified",
            "last_login",
            "date_joined",
        )



class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    timezone = serializers.ChoiceField(
        choices=[(tz, tz) for tz in ALL_TIMEZONES],
        default="Asia/Kolkata",
        initial="Asia/Kolkata",
    )

    class Meta:
        model = User
        fields = (
            "username",
            "email",
            "password",
            "timezone",
        )

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
            password=validated_data["password"],
            role=User.Role.DEVELOPER,
            timezone=validated_data.get("timezone", "Asia/Kolkata"),
            email_verified=False,
            is_active=True,
        )

        EmailVerificationToken.objects.create(user=user)
        return user




class VerifyEmailSerializer(serializers.Serializer):
    token = serializers.UUIDField()



class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        user = authenticate(
            username=attrs["username"],
            password=attrs["password"],
        )

        if not user:
            raise serializers.ValidationError("Invalid credentials")

        attrs["user"] = user
        return attrs



class RefreshSerializer(serializers.Serializer):
    refresh = serializers.CharField()

class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()