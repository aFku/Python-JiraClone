import uuid

from rest_framework import status
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK
from rest_framework import permissions

from django.db.models import Exists, OuterRef
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend

from .filters import TaskFilter, CommentFilter
from .models import Task, Comment, TaskObserver
from .serializers import (TaskSerializer, TaskCreateSerializer, TaskUpdateSerializer, CommentSerializer,
                          CommentCreateSerializer, CommentUpdateSerializer,
                          TaskObserverSerializer)

from permissions.project_permissions import IsDeveloperOrDeny, IsViewerOrDeny, IsAdminOrDeny
from projects_app.models import ProjectMember


class TasksView(generics.ListCreateAPIView):
    """
    Class for List / Create Tasks
    GET - Fetch list of accessible tasks (for viewers)
    POST - Create Task (for devs and admins)
    """

    queryset = Task.objects.all()
    filter_backends = [DjangoFilterBackend]
    filterset_class = TaskFilter
    methods_permissions_classes = {
        'POST': [IsDeveloperOrDeny]
    }

    def get_queryset(self):
        """
        Optimized solution to filter out tasks in projects that user should not see.
        Creating additional column with annotate that will have True/False regarding if ProjectMember has line
        with task project and user's ID
        """
        user_id = self.get_user_id()
        return Task.objects.annotate(
            is_member=Exists(
                ProjectMember.objects.filter(
                    project=OuterRef('project_id'),
                    user=user_id
                )
            )
        ).filter(is_member=True)

    def get_user_id(self):
        return self.request.headers.get('user_id') # TO DO: Change when user id correctly handled

    def get_permissions(self):
        permission_classes = [permissions.IsAuthenticated]
        permission_classes += self.methods_permission_classes.get(self.request.method, [])
        return [p() for p in permission_classes]

    def get_serializer_class(self):
        if self.request.method == "GET":
            return TaskSerializer
        if self.request.method == "POST":
            return TaskCreateSerializer
        return super().get_serializer_class()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            data=request.data,
            context={'user_id': uuid.uuid4()}
        )  #  TO DO: replace with real user id later
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        response_details = TaskSerializer(instance=serializer.instance)
        headers = self.get_success_headers(serializer.data)
        return Response(response_details.data, status=status.HTTP_201_CREATED, headers=headers)


class TaskByIdView(generics.RetrieveUpdateDestroyAPIView):
    """
    View for managing single task
    GET - Get task details (for viewers)
    PATCH - Update partially task (for devs and admins)
    DELETE - Remove task (for admins
    """


    queryset = Task.objects.all()
    lookup_field = 'id'
    lookup_url_kwarg = 'task_pk'
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
        if self.request.method in ['GET', 'DELETE']:
            return TaskSerializer
        if self.request.method == 'PATCH':
            return TaskUpdateSerializer
        return super().get_serializer_class()

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)

        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        response_details = TaskSerializer(instance=serializer.instance)
        return Response(response_details.data, status=status.HTTP_200_OK)



class CommentListCreateView(generics.ListCreateAPIView):
    """
    View for List / Create comments related to specific task
    GET - Get all comments for given task
    POST - Create new comment for given task
    """

    filter_backends = [DjangoFilterBackend]
    filterset_class = CommentFilter
    methods_permissions_classes = {
        'POST': [IsDeveloperOrDeny]
    }

    def get_queryset(self):
        """
        Optimized solution to filter out comments in projects that user should not see.
        Creating additional column with annotate that will have True/False regarding if ProjectMember has line
        with comment project and user's ID
        """
        user_id = self.get_user_id()
        return Comment.objects.annotate(
            is_member=Exists(
                ProjectMember.objects.filter(
                    project=OuterRef('project_id'),
                    user=user_id
                )
            )
        ).filter(is_member=True)

    def get_user_id(self):
        return self.request.headers.get('user_id') # TO DO: Change when user id correctly handled

    def get_permissions(self):
        permission_classes = [permissions.IsAuthenticated]
        permission_classes += self.methods_permission_classes.get(self.request.method, [])
        return [p() for p in permission_classes]

    def get_queryset(self):
        task_pk = self.kwargs["task_pk"]
        task = get_object_or_404(Task, pk=task_pk)
        comments = Comment.objects.filter(task=task)
        return comments

    def get_serializer_class(self):
        if self.request.method == "GET":
            return CommentSerializer
        if self.request.method == "POST":
            return CommentCreateSerializer
        return super().get_serializer_class()

    def perform_create(self, serializer):
        task_pk = self.kwargs["task_pk"]
        task = get_object_or_404(Task, pk=task_pk)
        serializer.save(
            task=task,
            user_id=uuid.uuid4() #  TO DO: replace with real user id later
        )


class CommentByIdView(generics.RetrieveUpdateDestroyAPIView):
    """
    View for managing existing comment
    GET - Get comment details
    PATCH - Edit comment
    DELETE - Remove comment
    """

    queryset = Comment.objects.all()
    lookup_field = 'id'
    lookup_url_kwarg = 'comment_pk'
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
        if self.request.method in ['GET', 'DELETE']:
            return CommentSerializer
        if self.request.method == 'PATCH':
            return CommentUpdateSerializer
        return super().get_serializer_class()

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)

        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        response_details = CommentSerializer(instance=serializer.instance)
        return Response(response_details.data, status=HTTP_200_OK)


class TaskObserversView(APIView):
    """
    View for managing observers inside task
    GET - List all observers in task
    POST - Add observer to task (Current user only)
    DELETE - Remove observer from task (Current user only)
    """

    permission_classes = [IsAuthenticated, IsViewerOrDeny]

    def get_user_id(self, request):
        return request.headers.get('user_id') # TO DO: Change when user id correctly handled

    def get_task(self, request, task_pk):
        obj = get_object_or_404(Task, id=task_pk)
        self.check_object_permissions(request, obj)
        return obj

    def get(self, request, task_pk):
        task = self.get_task(request, task_pk)
        task_observers = task.observers.all()
        serializer = TaskObserverSerializer(task_observers, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, task_pk):
        task = self.get_task(request, task_pk)
        serializer = TaskObserverSerializer(
            data={},
            context={
                "task": task,
                "user_id": self.get_user_id(request) #  TO DO: replace with real user id later
            }
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, task_pk):
        task = self.get_task(request, task_pk)
        user_id = self.get_user_id(request) #  TO DO: replace with real user id later
        if not user_id:
            return Response({"error": "Missing user_id parameter"}, status=status.HTTP_400_BAD_REQUEST) # Remove after TO DO
        deleted, _ = TaskObserver.objects.filter(task=task, user_id=user_id).delete()
        if deleted:
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({"error": "Observer not found"}, status=status.HTTP_404_NOT_FOUND)
