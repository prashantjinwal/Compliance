import threading

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework_simplejwt.tokens import RefreshToken

try:
    from drf_spectacular.utils import extend_schema, OpenApiParameter
except ImportError:
    def extend_schema(*args, **kwargs):
        def decorator(view_method):
            return view_method
        return decorator
    OpenApiParameter = None

from .models import User, Organization, Role
from .serializers import (
    RegisterSerializer,
    LoginSerializer,
    UserSerializer,
    UserUpdateSerializer,
    OrganizationSerializer,
    OrganizationUpdateSerializer,
    RoleSerializer,
)
from audit.utils import log_action


class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    @extend_schema(
        request=RegisterSerializer,
        responses={201: UserSerializer},
        description=(
            "Register a new user and organization. "
            "Seeds default roles (Admin, Legal, IT, Finance, Auditor, Compliance)."
        ),
        tags=["Auth"],
    )
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        log_action(
            user=user,
            action="user_login",
            entity_type="User",
            entity_id=str(user.id),
            description=f"User registered: {user.email}",
            organization=user.organization,
            request=request,
        )
        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    @extend_schema(
        request=LoginSerializer,
        responses={
            200: {
                "type": "object",
                "properties": {
                    "access": {"type": "string"},
                    "refresh": {"type": "string"},
                    "user": {"type": "object"},
                },
            }
        },
        description="Authenticate and receive JWT tokens.",
        tags=["Auth"],
    )
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data
        refresh = RefreshToken.for_user(user)
        log_action(
            user=user,
            action="user_login",
            entity_type="User",
            entity_id=str(user.id),
            description=f"User logged in: {user.email}",
            organization=user.organization,
            request=request,
        )
        return Response({
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "user": UserSerializer(user).data,
        })


class MeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        responses={200: UserSerializer},
        description="Get current authenticated user profile.",
        tags=["Auth"],
    )
    def get(self, request):
        return Response(UserSerializer(request.user).data)

    @extend_schema(
        request=UserUpdateSerializer,
        responses={200: UserSerializer},
        description="Update current user's profile (full_name).",
        tags=["Auth"],
    )
    def patch(self, request):
        serializer = UserUpdateSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(UserSerializer(request.user).data)


class OrganizationDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        responses={200: OrganizationSerializer},
        description="Get current user's organization details.",
        tags=["Organization"],
    )
    def get(self, request):
        return Response(OrganizationSerializer(request.user.organization).data)

    @extend_schema(
        request=OrganizationUpdateSerializer,
        responses={200: OrganizationSerializer},
        description=(
            "Update organization settings: name, industry, regions, "
            "configured_sources, risk_mapping_rules."
        ),
        tags=["Organization"],
    )
    def patch(self, request):
        serializer = OrganizationUpdateSerializer(
            request.user.organization, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(OrganizationSerializer(request.user.organization).data)


class RoleListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        responses={200: RoleSerializer(many=True)},
        description="List all available roles in the system.",
        tags=["Organization"],
    )
    def get(self, request):
        roles = Role.objects.all()
        return Response(RoleSerializer(roles, many=True).data)
