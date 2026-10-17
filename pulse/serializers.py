from rest_framework import serializers
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from .models import UserProfile, PriceAlert, NotificationLog


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['role', 'created_at']


class UserSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'profile']


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)
    access = serializers.SerializerMethodField()
    role = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'access', 'role']

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user

    def get_access(self, obj):
        refresh = RefreshToken.for_user(obj)
        return str(refresh.access_token)

    def get_role(self, obj):
        return obj.profile.role

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError('Username already exists')
        return value


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
    access = serializers.SerializerMethodField(read_only=True)

    def get_access(self, obj):
        user = obj.get('user')
        if user:
            refresh = RefreshToken.for_user(user)
            return str(refresh.access_token)
        return None


class PriceAlertSerializer(serializers.ModelSerializer):
    route = serializers.SerializerMethodField()

    class Meta:
        model = PriceAlert
        fields = ['id', 'route', 'origin', 'destination', 'threshold_price', 'status', 'created_at']
        read_only_fields = ['id', 'created_at', 'status']

    def get_route(self, obj):
        return f'{obj.origin}-{obj.destination}'


class NotificationLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationLog
        fields = ['id', 'alert', 'triggered_price', 'message', 'notified_at']
        read_only_fields = ['id', 'notified_at']
