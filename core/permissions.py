from rest_framework.permissions import BasePermission


def get_user_role(user):
    profile = getattr(user, 'user_profile', None)
    return getattr(profile, 'role', None)


def get_user_school(user):
    profile = getattr(user, 'user_profile', None)
    return getattr(profile, 'school', None)


class IsHQ(BasePermission):
    def has_permission(self, request, view):
        return get_user_role(request.user) == 'HQ'


class IsPrincipalOrHQ(BasePermission):
    def has_permission(self, request, view):
        return get_user_role(request.user) in {'HQ', 'PRINCIPAL'}


class IsTeacherOrAbove(BasePermission):
    def has_permission(self, request, view):
        return get_user_role(request.user) in {'HQ', 'PRINCIPAL', 'TEACHER'}
