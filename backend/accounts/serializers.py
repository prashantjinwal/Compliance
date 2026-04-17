from rest_framework import serializers
from .models import User, Organization, Role
from django.contrib.auth import authenticate


class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = "__all__"


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = "__all__"


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    organization = OrganizationSerializer()

    class Meta:
        model = User
        fields = ["email", "password", "full_name", "organization"]

    def create(self, validated_data):
        org_data = validated_data.pop("organization")
        organization = Organization.objects.create(**org_data)

        # default role
        role = Role.objects.filter(name="Admin").first()

        user = User.objects.create_user(
            email=validated_data["email"],
            password=validated_data["password"],
            full_name=validated_data["full_name"],
            organization=organization,
            role=role
        )

        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, data):
        user = authenticate(email=data["email"], password=data["password"])
        if not user:
            raise serializers.ValidationError("Invalid credentials")
        return user


class UserSerializer(serializers.ModelSerializer):
    organization = OrganizationSerializer()
    role = RoleSerializer()

    class Meta:
        model = User
        fields = ["id", "email", "full_name", "organization", "role"]
