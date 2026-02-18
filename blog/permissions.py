from rest_framework import permissions

class IsABloggerPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.groups.filter(name='bloggers').exists()


class IsAdminOrOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user.is_staff or obj.author == request.user