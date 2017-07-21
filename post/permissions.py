from rest_framework import permissions

class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow poster to update the post
    """

    def has_object_permission(selfs, request, view, obj):
        # Read permissions are allowed (GET, HEAD and OPTIONS)
        if request.method in permissions.SAFE_METHODS:
            return True

        owner_field = 'owner'
        if hasattr(type(obj), 'OWNER_FIELD'):
            owner_field = getattr(obj, type(obj).OWNER_FIELD)

        if not hasattr(obj, owner_field):
            return False

        return getattr(obj, owner_field) == request.user