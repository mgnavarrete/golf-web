from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .serializers_auth import MeSerializer


@api_view(["GET", "PATCH"])
@permission_classes([IsAuthenticated])
def me(request):
    if request.method == "GET":
        return Response(MeSerializer.from_user(request.user))

    user = request.user
    data = request.data

    if "first_name" in data:
        user.first_name = data["first_name"]
    if "last_name" in data:
        user.last_name = data["last_name"]

    if "email" in data:
        email = data["email"]
        if email != user.email:
            from .models import User

            if User.objects.filter(email=email).exclude(id=user.id).exists():
                return Response(
                    {"detail": "Este correo electrónico ya está en uso."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            user.email = email

    if "profile_icon" in data:
        icon = data["profile_icon"]
        if isinstance(icon, int) and 1 <= icon <= 10:
            user.profile_icon = icon
        else:
            return Response(
                {"detail": "El icono debe ser un número entre 1 y 10."},
                status=status.HTTP_400_BAD_REQUEST,
            )

    user.save()
    return Response(MeSerializer.from_user(user))


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def change_password(request):
    user = request.user
    old_password = request.data.get("old_password")
    new_password = request.data.get("new_password")

    if not old_password or not new_password:
        return Response(
            {"detail": "Debes proporcionar la contraseña actual y la nueva contraseña."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if not user.check_password(old_password):
        return Response(
            {"detail": "La contraseña actual es incorrecta."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        validate_password(new_password, user)
    except DjangoValidationError as e:
        return Response({"detail": " ".join(e.messages)}, status=status.HTTP_400_BAD_REQUEST)

    user.set_password(new_password)
    user.save()

    return Response({"detail": "Contraseña cambiada exitosamente."}, status=status.HTTP_200_OK)
