from rest_framework import permissions


class IsAdmin(permissions.BasePermission):
    """
    Allows access only to admin users.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == 'ADMIN'


class IsTeacher(permissions.BasePermission):
    """
    Allows access only to teacher users.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == 'TEACHER'


class IsStudent(permissions.BasePermission):
    """
    Allows access only to student users.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == 'STUDENT'


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    The request is authenticated as an admin user, or is a read-only request.
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated
        return request.user and request.user.is_authenticated and request.user.role == 'ADMIN'


class IsAdminOrTeacher(permissions.BasePermission):
    """
    Allows access to admin or teacher users.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role in ['ADMIN', 'TEACHER']


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Allows a user to edit/delete their own objects, or allows admin to edit any object.
    """
    def has_object_permission(self, request, view, obj):
        if hasattr(obj, 'student'):
            # For Submission objects
            return obj.student == request.user or request.user.role == 'ADMIN'
        elif hasattr(obj, 'username'):
            # For User objects
            return obj == request.user or request.user.role == 'ADMIN'
        return request.user.role == 'ADMIN'
