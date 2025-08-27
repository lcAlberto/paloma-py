from rest_framework import permissions
from .models import FarmUser

class IsOwnerPermission(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        try:
            farm_user = FarmUser.objects.get(farm=obj, user=request.user)
            return farm_user.is_owner
        except FarmUser.DoesNotExist:
            return False