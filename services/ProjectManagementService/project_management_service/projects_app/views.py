from django.db import transaction
from django.db.models import Exists, OuterRef
from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework import generics
from rest_framework import permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError

from .models import Project
from .models import ProjectMember
from permissions.project_permissions import IsViewerOrDeny, IsAdminOrDeny
from .serializers import ProjectSerializer, ProjectMemberSerializer, ProjectMemberRemoveSerializer



class ProjectsView(generics.ListCreateAPIView):
    """
    View for managing Projects (Create/Fetch All)
    List - Default fetch. Will only see projects where user is member
    Create - Default create (id field read_only in serializer). Each user can create their own project
    """

    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        Optimized solution to filter out projects that user should not see.
        Looking inside database, in which projects user is member (any role)
        """
        user_id = self.get_user_id()
        return Project.objects.filter(
            Exists(
                ProjectMember.objects.filter(
                    project=OuterRef('pk'),
                    user_id=user_id
                )
            )
        )

    def get_user_id(self):
        return self.request.headers.get('user_id') # TO DO: Change when user id correctly handled

    def perform_create(self, serializer):
        user_id = self.get_user_id()
        if not user_id:
            raise ValidationError({"user_id": "Header 'user_id' cannot be empty."})

        with transaction.atomic():
            project = serializer.save()
            member_serializer = ProjectMemberSerializer(
                data={
                    "user_id": user_id,
                    "role": ProjectMember.Role.ADMIN,
                },
                context={
                    "project": project
                }
            )
            member_serializer.is_valid(raise_exception=True)
            member_serializer.save()
        return project



class ProjectByIdView(generics.RetrieveUpdateDestroyAPIView):
    """
    Default methods for projects:
    - Fetch: For viewers
    - Update: For Admins
    - Delete: For Admins
    """

    serializer_class = ProjectSerializer
    http_method_names = ['get', 'patch', 'delete']
    methods_permission_classes = {
        'GET': [IsViewerOrDeny],
        'PATCH': [IsAdminOrDeny],
        'DELETE': [IsAdminOrDeny]
    }

    def get_permissions(self):
        permission_classes = [permissions.IsAuthenticated]
        permission_classes += self.methods_permission_classes.get(self.request.method, [])
        return [p() for p in permission_classes]


class ProjectMembersView(APIView):
    """
    Custom APIView for managing project members. Project ID is required for all methods
    GET - Get list of members in specific projects. Accessible for viewers
    POST - Add one or many members to project. Accessible for Admins
    DELETE - Remove members from project. Accessible for Admins
    """
    methods_permission_classes = {
        'GET': [IsViewerOrDeny],
        'POST': [IsAdminOrDeny],
        'DELETE': [IsAdminOrDeny]
    }

    def get_permissions(self):
        permission_classes = [permissions.IsAuthenticated]
        permission_classes += self.methods_permission_classes.get(self.request.method, [])
        return [p() for p in permission_classes]

    def get(self, request, project_id):
        project = get_object_or_404(Project, id=project_id)
        role_param = request.query_params.get('role', None)
        members = project.get_members(role_param)
        serializer = ProjectMemberSerializer(members, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, project_id):
        project = get_object_or_404(Project, id=project_id)
        serializer = ProjectMemberSerializer(
            data=request.data,
            many=True,
            context={"project": project}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, project_id):
        project = get_object_or_404(Project, id=project_id)
        serializer = ProjectMemberRemoveSerializer(
            data=request.data,
            context={"project": project}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
