from rest_framework import permissions

class IsAdmin(permissions.BasePermission):
    """
    Permission class to allow only admin users to access the view.
    """
    def has_permission(self, request, view):
        return request.user.is_staff


class IsMarketer(permissions.BasePermission):
    """
    Permission class to allow only marketer and admin users to access the view.
    """
    def has_permission(self, request, view):
        return (
            request.user.groups.filter(name='Marketer').exists() or
            request.user.is_staff
        )
    

class IsLearner(permissions.BasePermission):
    """
    Permission class to allow only learner, marketer and admin users to access the view.
    """
    def has_permission(self, request, view):
        return (
            request.user.groups.filter(name='Learner').exists() or
            request.user.groups.filter(name='Marketer').exists() or
            request.user.is_staff
        )
    



class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Permission class to allow admin users to edit the view and others to read it.
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_staff