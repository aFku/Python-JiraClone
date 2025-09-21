from rest_framework.views import csrf_exempt
from rest_framework.decorators import api_view
from django.http import JsonResponse
from rest_framework.parsers import JSONParser
from rest_framework import status

from .models import Sprint
from .serializers import SprintsSerializer, SprintCreateSerializer, SprintUpdateSerializer
from .filters import SprintFilter


@csrf_exempt
@api_view(['GET', 'POST'])
def sprints_view(request):
    if request.method == 'GET':
        sprints = Sprint.objects.all()
        filterset = SprintFilter(request.GET, queryset=sprints)
        if filterset.is_valid():
            sprints = filterset.qs
        serializer = SprintsSerializer(sprints, many=True)
        return JsonResponse(serializer.data, safe=False)

    elif request.method == 'POST':
        data = JSONParser().parse(request)
        serializer = SprintCreateSerializer(data=data)
        if serializer.is_valid():
            object = serializer.save()
            read_serializer = SprintsSerializer(object)
            return JsonResponse(read_serializer.data, status=status.HTTP_201_CREATED)
        return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@csrf_exempt
@api_view(['GET', 'PATCH', 'DELETE'])
def sprint_by_id_view(request, sprint_pk):
    try:
        sprint = Sprint.objects.get(id=sprint_pk)
    except Sprint.DoesNotExist:
        return JsonResponse({"error": "Sprint not found"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = SprintsSerializer(sprint)
        return JsonResponse(serializer.data)

    elif request.method == 'PATCH':
        data = JSONParser().parse(request)
        serializer = SprintUpdateSerializer(sprint, data=data, partial=True)
        if serializer.is_valid():
            object = serializer.save()
            read_serializer = SprintsSerializer(object)
            return JsonResponse(read_serializer.data)
        return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        sprint.delete()
        return JsonResponse({}, status=status.HTTP_204_NO_CONTENT)


