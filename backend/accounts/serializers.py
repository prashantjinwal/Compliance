from django.contrib.auth import authenticate
from rest_framework import serializers

from .models import Organization, Role, User


class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = [
            "id", "name", "industry", "country", "regions",
            "configured_sources", "risk_mapping_rules", "created_at", "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class OrganizationUpdateSerializer(serializers.ModelSerializer):
    """Used for PATCH /api/auth/organization/ — partial updates."""
    class Meta:
        model = Organization
        fields = ["name", "industry", "country", "regions", "configured_sources", "risk_mapping_rules"]


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ["id", "name", "description"]


class RegisterSerializer(serializers.Serializer):
    first_name = serializers.CharField(max_length=150)
    last_name = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)
    organization = serializers.CharField(max_length=255)
    username = serializers.EmailField(write_only=True)

    def validate(self, attrs):
        email = attrs["email"].strip().lower()
        username = attrs["username"].strip().lower()
        first_name = attrs["first_name"].strip()
        last_name = attrs["last_name"].strip()
        organization = attrs["organization"].strip()

        if email != username:
            raise serializers.ValidationError(
                {"username": "Username must match the email address."}
            )

        if attrs["password"] != attrs["confirm_password"]:
            raise serializers.ValidationError(
                {"confirm_password": "Passwords do not match."}
            )

        if not first_name:
            raise serializers.ValidationError(
                {"first_name": "First name is required."}
            )

        if not last_name:
            raise serializers.ValidationError(
                {"last_name": "Last name is required."}
            )

        if not organization:
            raise serializers.ValidationError(
                {"organization": "Organization is required."}
            )

        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError(
                {"email": "A user with this email already exists."}
            )

        attrs["email"] = email
        attrs["username"] = username
        attrs["first_name"] = first_name
        attrs["last_name"] = last_name
        attrs["organization"] = organization
        return attrs

    def create(self, validated_data):
        validated_data.pop("confirm_password")
        validated_data.pop("username")

        # Always seed default roles for the new org
        _seed_default_roles()

        organization_name = validated_data.pop("organization")
        first_name = validated_data.pop("first_name")
        last_name = validated_data.pop("last_name")
        full_name = (first_name + " " + last_name).strip()

        organization = Organization.objects.filter(
            name__iexact=organization_name
        ).first()
        if organization is None:
            organization = Organization.objects.create(
                name=organization_name,
                industry="Not specified",
                country="Not specified",
            )

        role = Role.objects.filter(name__iexact="Admin").first()

        user = User.objects.create_user(
            email=validated_data["email"],
            password=validated_data["password"],
            full_name=full_name,
            organization=organization,
            role=role,
        )
        return user


class LoginSerializer(serializers.Serializer):
    username = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        username = data["username"].strip().lower()
        user = authenticate(username=username, password=data["password"])
        if not user:
            raise serializers.ValidationError({"detail": "Invalid credentials."})
        if not user.is_active:
            raise serializers.ValidationError({"detail": "User account is disabled."})
        return user


class UserSerializer(serializers.ModelSerializer):
    organization = OrganizationSerializer(read_only=True)
    role = RoleSerializer(read_only=True)

    class Meta:
        model = User
        fields = ["id", "email", "full_name", "organization", "role", "date_joined"]
        read_only_fields = ["id", "date_joined"]


class UserUpdateSerializer(serializers.ModelSerializer):
    """Partial update of the authenticated user profile."""
    class Meta:
        model = User
        fields = ["full_name"]


def _seed_default_roles():
    """Ensure every installation has the standard role set."""
    default_roles = [
        ("Admin", "Full administrative access"),
        ("Legal", "Legal team — reviews regulations and notes"),
        ("IT", "IT team — handles technical compliance tasks"),
        ("Finance", "Finance team — handles financial compliance"),
        ("Auditor", "Read-only audit access"),
        ("Compliance", "General compliance officer"),
    ]
    for name, desc in default_roles:
        Role.objects.get_or_create(name=name, defaults={"description": desc})
