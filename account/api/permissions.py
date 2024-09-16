from rest_framework import permissions
from django.utils.translation import gettext as _
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import SAFE_METHODS, BasePermission

from account.models import APIKey


class HasAPIKey(BasePermission):
    """
    Permission class to authenticate users with an API key.
    """
    def has_permission(self, request, view):
        """
        Check if the request contains a valid API key.
        """
        key = request.META.get("HTTP_API_KEY")
        if key and APIKey.verify_key(key):
            return True
        raise PermissionDenied(_("Not a valid API key."))

    def has_object_permission(self, request, view, obj):
        """
        Check object-level permissions, delegating to `has_permission`.
        """
        return self.has_permission(request, view)


class IsAdmin(BasePermission):
    """
    Permission class to allow only admin users to access the view.
    """
    def has_permission(self, request, view):
        """
        Check if the user is an admin.
        """
        return request.user.is_staff


class IsMarketer(BasePermission):
    """
    Permission class to allow only marketer and admin users to access the view.
    """
    def has_permission(self, request, view):
        """
        Check if the user is a marketer or admin.
        """
        return (
            request.user.groups.filter(name='Marketer').exists() or
            request.user.is_marketer
        )


class IsLearner(BasePermission):
    """
    Permission class to allow only learner, marketer, and admin users to access the view.
    """
    def has_permission(self, request, view):
        """
        Check if the user is a learner, marketer, or admin.
        """
        return (
            request.user.groups.filter(name='Learner').exists() or
            request.user.is_student
        )


class IsAdminOrReadOnly(BasePermission):
    """
    Permission class to allow admin users to edit the view and others to read it.
    """
    def has_permission(self, request, view):
        """
        Allow read-only access for non-admin users.
        """
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_staff
