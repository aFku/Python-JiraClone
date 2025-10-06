from rest_framework import status
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from .serializers import ProjectSerializer, ProjectMemberSerializer, ProjectMemberRemoveSerializer
from .models import Project


class ProjectsView(generics.ListCreateAPIView):
    """
    View for managing Projects (Create/Fetch All)
    List - Default fetch
    Create - Default create (id field read_only in serializer)
    """

    queryset = Project.objects.all()
    serializer_class = ProjectSerializer


class ProjectByIdView(generics.RetrieveUpdateDestroyAPIView):
    """
    Default Create, Update, Delete for projects
    """

    serializer_class = ProjectSerializer


class ProjectMembersView(APIView):
    """
    Custom APIView for managing project members. Project ID is required for all methods
    GET - Get list of members in specific projects
    POST - Add one or many members to project
    DELETE - Remove members from project
    """

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
