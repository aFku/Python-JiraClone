import uuid

from rest_framework.status import HTTP_200_OK
from rest_framework.views import csrf_exempt, APIView
from rest_framework import status
from rest_framework import generics
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from .models import Task, Comment, TaskObserver
from .serializers import (TaskSerializer, TaskCreateSerializer, TaskUpdateSerializer, CommentSerializer,
                          CommentCreateSerializer, CommentUpdateSerializer,
                          TaskObserverSerializer)
from .filters import TaskFilter, CommentFilter


class TasksView(generics.ListCreateAPIView):
    """
    Class for List / Create Tasks
    GET - Fetch list of accessible tasks
    POST - Create Task
    """

    queryset = Task.objects.all()
    filter_backends = [DjangoFilterBackend]
    filterset_class = TaskFilter

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
    GET - Get task details
    PATCH - Update partially task
    DELETE - Remove task
    """


    queryset = Task.objects.all()
    lookup_field = 'id'
    lookup_url_kwarg = 'task_pk'
    http_method_names = ['get', 'patch', 'delete']

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

    def get_task(self, task_pk):
        return get_object_or_404(Task, id=task_pk)

    def get(self, request, task_pk):
        task = self.get_task(task_pk)
        task_observers = task.observers.all()
        serializer = TaskObserverSerializer(task_observers, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, task_pk):
        task = self.get_task(task_pk)
        serializer = TaskObserverSerializer(
            data={},
            context={
                "task": task,
                "user_id": uuid.uuid4() #  TO DO: replace with real user id later
            }
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, task_pk):
        task = self.get_task(task_pk)
        user_id = request.query_params.get('user_id') #  TO DO: replace with current user id later
        if not user_id:
            return Response({"error": "Missing user_id parameter"}, status=status.HTTP_400_BAD_REQUEST) # Remove after TO DO
        deleted, _ = TaskObserver.objects.filter(task=task, user_id=user_id).delete()
        if deleted:
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({"error": "Observer not found"}, status=status.HTTP_404_NOT_FOUND)
