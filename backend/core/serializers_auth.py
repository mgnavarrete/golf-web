from rest_framework import serializers


class MeSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    email = serializers.EmailField()
    first_name = serializers.CharField(allow_blank=True)
    last_name = serializers.CharField(allow_blank=True)
    is_active = serializers.BooleanField()
    is_staff = serializers.BooleanField()
    is_superuser = serializers.BooleanField()
    profile_icon = serializers.IntegerField()
    role = serializers.CharField()
    roles = serializers.ListField(child=serializers.CharField())
    permissions = serializers.DictField(child=serializers.BooleanField())

    @staticmethod
    def from_user(user):
        role = user.role if hasattr(user, "role") else "MIXED"
        permissions = user.get_effective_permissions() if hasattr(user, "get_effective_permissions") else {}
        if user.is_superuser:
            role = "ADMIN"

        return {
            "id": user.id,
            "email": user.email,
            "first_name": user.first_name or "",
            "last_name": user.last_name or "",
            "is_active": user.is_active,
            "is_staff": user.is_staff,
            "is_superuser": user.is_superuser,
            "profile_icon": user.profile_icon or 1,
            "role": role,
            "roles": [role],
            "permissions": permissions,
        }
