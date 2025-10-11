from rest_framework import status
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import permissions
from django_filters.rest_framework import DjangoFilterBackend

from .models import Sprint
from .serializers import SprintsSerializer, SprintCreateSerializer, SprintUpdateSerializer
from .filters import SprintFilter
from ..projects_app.permissions import IsViewerOrDeny, IsDeveloperOrDeny, IsAdminOrDeny


class SprintsView(generics.ListCreateAPIView):
    """
    View for managing Sprints (Create/Fetch All)
    List - handled by default (by viewers)
    Create - Custom implementation (Changing serializer for response) (for Devs and Admins)
    """

    queryset = Sprint.objects.all()
    filter_backends = [DjangoFilterBackend]
    filterset_class = SprintFilter
    methods_permissions_classes = {
        'GET': [IsViewerOrDeny],
        'POST': [IsDeveloperOrDeny]
    }

    def get_permissions(self):
        permission_classes = [permissions.IsAuthenticated]
        permission_classes += self.methods_permission_classes.get(self.request.method, [])
        return [p() for p in permission_classes]

    def get_serializer_class(self):
        if self.request.method == "GET":
            return SprintsSerializer
        if self.request.method == "POST":
            return SprintCreateSerializer
        return super().get_serializer_class()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        response_details = SprintsSerializer(instance=serializer.instance)
        headers = self.get_success_headers(serializer.data)
        return Response(response_details.data, status=status.HTTP_201_CREATED, headers=headers)


class SprintByIdView(generics.RetrieveUpdateDestroyAPIView):
    """
    Class for interacting with one specific sprint
    Get - handled by default (for viewers)
    Delete - handled by default (for admins)
    Patch - custom implementation. Using different serializers for update and response (for devs and admins)
    """

    queryset = Sprint.objects.all()
    lookup_field = 'id'
    lookup_url_kwarg = 'sprint_pk'
    http_method_names = ['get', 'patch', 'delete']
    methods_permissions_classes = {
        'GET': [IsViewerOrDeny],
        'PATCH': [IsDeveloperOrDeny],
        'DELETE': [IsAdminOrDeny]
    }

    def get_permissions(self):
        permission_classes = [permissions.IsAuthenticated]
        permission_classes += self.methods_permission_classes.get(self.request.method, [])
        return [p() for p in permission_classes]

    def get_serializer_class(self):
        if self.request.method in ["GET", "DELETE"]:
            return SprintsSerializer
        if self.request.method == "PATCH":
            return SprintUpdateSerializer
        return super().get_serializer_class()

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)

        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        response_details = SprintsSerializer(instance=serializer.instance)
        return Response(response_details.data, status=status.HTTP_200_OK)
