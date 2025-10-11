from rest_framework import permissions

from projects_app.models import ProjectMember
from utils.models_helpers import ProjectRelated


def get_project_from_object(obj: ProjectRelated):
    """
    Check if model has 'project' member and fetch project object
    """
    return obj.get_project()


class IsViewerOrDeny(permissions.BasePermission):
    """
    Class for checking if user is viewer member of Project
    """

    def has_object_permission(self, request, view, obj):
        project = get_project_from_object(obj)
        user_id = request.headers.get('user_id') # TO DO: When authentication implemented
        return ProjectMember.objects.filter(user_id=user_id, project=project).exists()


class IsDeveloperOrDeny(permissions.BasePermission):
    """
    Class for checking if user has at least developers permissions for specific project
    """

    def has_object_permission(self, request, view, obj):
        project = get_project_from_object(obj)
        user_id = request.headers.get('user_id')  # TO DO: When authentication implemented
        member = ProjectMember.objects.filter(user_id=user_id, project=project).first()
        if not member: return False
        return member.role in [ProjectMember.Role.ADMIN, ProjectMember.Role.DEVELOPER]


class IsAdminOrDeny(permissions.BasePermission):
    """
    Class for checking if user has at least developers permissions for specific project
    """

    def has_object_permission(self, request, view, obj):
        project = get_project_from_object(obj)
        user_id = request.headers.get('user_id')  # TO DO: When authentication implemented
        member = ProjectMember.objects.filter(user_id=user_id, project=project).first()
        if not member: return False
        return member.role in [ProjectMember.Role.ADMIN]