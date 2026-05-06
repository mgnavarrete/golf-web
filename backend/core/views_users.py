from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .permissions import require_app_permission
from .serializers import UserAdminCreateSerializer, UserAdminSerializer, UserAdminUpdateSerializer

User = get_user_model()


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def user_list_create(request):
    require_app_permission(request, "can_manage_users")

    if request.method == "GET":
        users = User.objects.all().order_by("id")
        return Response(UserAdminSerializer(users, many=True).data)

    serializer = UserAdminCreateSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    data = serializer.validated_data

    if User.objects.filter(email=data["email"]).exists():
        return Response({"detail": "Este email ya está registrado"}, status=status.HTTP_400_BAD_REQUEST)

    user = User.objects.create_user(
        email=data["email"],
        password=data["password"],
        first_name=data.get("first_name", ""),
        last_name=data.get("last_name", ""),
        profile_icon=data.get("profile_icon", 1),
        role=data.get("role", User.ROLE_MIXED),
        is_active=data.get("is_active", True),
    )

    if user.role == User.ROLE_ADMIN:
        user.is_staff = True

    overrides = data.get("permission_overrides")
    if isinstance(overrides, dict):
        user.permission_overrides = overrides

    user.save()
    return Response(UserAdminSerializer(user).data, status=status.HTTP_201_CREATED)


@api_view(["GET", "PATCH", "DELETE"])
@permission_classes([IsAuthenticated])
def user_detail(request, pk):
    require_app_permission(request, "can_manage_users")

    try:
        user = User.objects.get(pk=pk)
    except User.DoesNotExist:
        return Response({"detail": "Usuario no encontrado"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == "GET":
        return Response(UserAdminSerializer(user).data)

    if request.method == "PATCH":
        serializer = UserAdminUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        if "email" in data and data["email"] != user.email:
            if User.objects.filter(email=data["email"]).exclude(pk=user.pk).exists():
                return Response({"detail": "Este email ya está registrado"}, status=status.HTTP_400_BAD_REQUEST)
            user.email = data["email"]

        for field in ["first_name", "last_name", "is_active", "profile_icon", "role"]:
            if field in data:
                setattr(user, field, data[field])

        if "password" in data and data["password"]:
            user.set_password(data["password"])

        if "permission_overrides" in data:
            user.permission_overrides = data["permission_overrides"]

        if user.role == User.ROLE_ADMIN:
            user.is_staff = True
        elif not user.is_superuser:
            user.is_staff = False

        user.save()
        return Response(UserAdminSerializer(user).data)

    if user.id == request.user.id:
        return Response({"detail": "No puedes eliminar tu propio usuario"}, status=status.HTTP_400_BAD_REQUEST)

    user.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)
