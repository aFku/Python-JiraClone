import uuid

from rest_framework.views import csrf_exempt
from rest_framework.decorators import api_view
from django.http import JsonResponse
from rest_framework.parsers import JSONParser
from rest_framework import status

from .models import Task, Comment
from .serializers import (TaskSerializer, TaskCreateSerializer, TaskUpdateSerializer, CommentSerializer,
                          CommentCreateSerializer, CommentUpdateSerializer)


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
def tasks_by_id_view(request, pk):
    try:
        task = Task.objects.get(id=pk)
    except Task.DoesNotExist:
        return JsonResponse({"errors": f'Task {pk} does not exists'}, status=status.HTTP_404_NOT_FOUND)

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
def comments_by_task(request, pk):
    try:
        task = Task.objects.get(id=pk)
    except Task.DoesNotExist:
        return JsonResponse({"errors": f'Task {pk} does not exists'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        comments = Comment.objects.filter(task=task)
        serializer = CommentSerializer(comments, many=True)
        return JsonResponse(serializer.data)
    elif request.method == 'POST':
        data = JSONParser().parse(request)
        serializer = CommentCreateSerializer(data=data)
        if serializer.is_valid():
            obj = serializer.save()
            read_serializer = CommentSerializer(obj)
            return JsonResponse(read_serializer.data)
        return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@csrf_exempt
@api_view(['GET', 'PATCH', 'DELETE'])
def comment_by_task_and_id(request, task_pk, comment_pk):
    pass

