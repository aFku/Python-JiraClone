import uuid

from rest_framework.views import csrf_exempt
from rest_framework.decorators import api_view
from django.http import JsonResponse
from rest_framework.parsers import JSONParser
from rest_framework import status

from .models import Task, Comment, TaskObserver
from .serializers import (TaskSerializer, TaskCreateSerializer, TaskUpdateSerializer, CommentSerializer,
                          CommentCreateSerializer, CommentUpdateSerializer,
                          TaskObserverSerializer)


@csrf_exempt
@api_view(['GET', 'POST'])
def tasks_view(request):
    if request.method == 'GET':
        tasks = Task.objects.all()
        serializer = TaskSerializer(tasks, many=True)
        return JsonResponse(serializer.data, safe=False)
    elif request.method == 'POST':
        data = JSONParser().parse(request)
        serializer = TaskCreateSerializer(data=data, context={'user_id': uuid.uuid4()}) #  replace with real user id later
        if serializer.is_valid():
            obj = serializer.save()
            read_serializer = TaskSerializer(obj)
            return JsonResponse(read_serializer.data)
        return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



@csrf_exempt
@api_view(['GET', 'PATCH', 'DELETE'])
def tasks_by_id_view(request, task_pk):
    try:
        task = Task.objects.get(id=task_pk)
    except Task.DoesNotExist:
        return JsonResponse({"errors": f'Task {task_pk} does not exists'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = TaskSerializer(task)
        return JsonResponse(serializer.data)
    elif request.method == 'PATCH':
        data = JSONParser().parse(request)
        serializer = TaskUpdateSerializer(instance=task, data=data, partial=True)
        if serializer.is_valid():
            obj = serializer.save()
            read_serializer = TaskSerializer(obj)
            return JsonResponse(read_serializer.data)
        return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'DELETE':
        task.delete()
        return JsonResponse({}, status=status.HTTP_204_NO_CONTENT)


@csrf_exempt
@api_view(['GET', 'POST'])
def comments_by_task(request, task_pk):
    try:
        task = Task.objects.get(id=task_pk)
    except Task.DoesNotExist:
        return JsonResponse({"errors": f'Task {task_pk} does not exists'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        comments = Comment.objects.filter(task=task)
        serializer = CommentSerializer(comments, many=True)
        return JsonResponse(serializer.data, safe=False)
    elif request.method == 'POST':
        data = JSONParser().parse(request)
        serializer = CommentCreateSerializer(data=data, context={"user_id": uuid.uuid4(), "task": task})
        if serializer.is_valid():
            obj = serializer.save()
            read_serializer = CommentSerializer(obj)
            return JsonResponse(read_serializer.data)
        return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@csrf_exempt
@api_view(['GET', 'PATCH', 'DELETE'])
def comment_by_id(request, comment_pk):
    try:
        comment = Comment.objects.get(id=comment_pk)
    except Comment.DoesNotExist:
        return JsonResponse({"errors": f'Comment {comment_pk} does not exists'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = CommentSerializer(comment)
        return JsonResponse(serializer.data)

    elif request.method == 'PATCH':
        data = JSONParser().parse(request)
        serializer = CommentUpdateSerializer(instance=comment, data=data, partial=True)
        if serializer.is_valid():
            obj = serializer.save()
            read_serializer = CommentSerializer(obj)
            return JsonResponse(read_serializer.data)
        return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        comment.delete()
        return JsonResponse({}, status=status.HTTP_204_NO_CONTENT)


@csrf_exempt
@api_view(['GET', 'POST', 'DELETE'])
def task_observers(request, task_pk):
    try:
        task = Task.objects.get(id=task_pk)
    except Task.DoesNotExist:
        return JsonResponse({"errors": f'Task {task_pk} does not exists'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        observers = task.observers
        serializer = TaskObserverSerializer(observers, many=True)
        return JsonResponse(serializer.data, safe=False)

    elif request.method == 'POST':
        serializer = TaskObserverSerializer(data={}, context={"user_id": uuid.uuid4(), "task": task})
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data, status=status.HTTP_201_CREATED, safe=False)
        else:
            return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        user_id = "PLACEHOLDER" # TO DO
        deleted, _ = TaskObserver.objects.filter(task=task, user_id=user_id).delete()
        if deleted:
            return JsonResponse({}, status=status.HTTP_204_NO_CONTENT)
        else:
            return JsonResponse({"error": "Observer not found"}, status=status.HTTP_404_NOT_FOUND)
