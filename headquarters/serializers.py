from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import UserProfile

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    role = serializers.ChoiceField(choices=UserProfile.ROLE_CHOICES)
    school_id = serializers.IntegerField(required=False, allow_null=True)
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'first_name', 'last_name', 'role', 'school_id']
        read_only_fields = ['id']

    def create(self, validated_data):
        role = validated_data.pop('role')
        school_id = validated_data.pop('school_id', None)
        password = validated_data.pop('password')

        user = User(**validated_data)
        user.set_password(password)
        user.save()

        profile = user.user_profile
        profile.role = role
        if school_id:
            profile.school_id = school_id
        profile.save()
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    role = serializers.CharField(source='user_profile.role')
    school_id = serializers.IntegerField(source='user_profile.school_id', allow_null=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'role', 'school_id']
