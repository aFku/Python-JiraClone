from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser
from rest_framework import status
from rest_framework.decorators import api_view

from .serializers import ProjectSerializer, ProjectMemberSerializer, ProjectMemberRemoveSerializer
from .models import Project


@csrf_exempt
@api_view(['GET', 'POST'])
def projects(request):
    if request.method == 'GET':
        projects = Project.objects.all()
        serializer = ProjectSerializer(projects, many=True)
        return JsonResponse(serializer.data, safe=False)

    elif request.method == 'POST':
        data = JSONParser().parse(request)
        serializer = ProjectSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data, status=status.HTTP_201_CREATED)
        return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@csrf_exempt
@api_view(['GET', 'PATCH', 'DELETE'])
def project_by_id(request, project_pk):
    try:
        project = Project.objects.get(id=project_pk)
    except Project.DoesNotExist:
        return JsonResponse({"error": "Project not found"}, status=status.HTTP_404_NOT_FOUND)


    if request.method == 'GET':
        serializer = ProjectSerializer(project)
        return JsonResponse(serializer.data, safe=False)

    elif request.method == 'PATCH':
        data = JSONParser().parse(request)
        data.pop('id', None)
        serializer = ProjectSerializer(project, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data)
        return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        project.delete()
        return JsonResponse({}, status=status.HTTP_204_NO_CONTENT)


@csrf_exempt
@api_view(['GET', 'POST', 'DELETE'])
def project_members(request, project_pk):
    try:
        project = Project.objects.get(id=project_pk)
    except Project.DoesNotExist:
        return JsonResponse({"error": "Project not found"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        role_param = request.query_params.get('role', None)
        serializer = ProjectMemberSerializer(project.get_members(role_param), many=True)
        return JsonResponse(serializer.data, safe=False)

    elif request.method == 'POST':
        data = JSONParser().parse(request)
        serializer = ProjectMemberSerializer(data=data, many=True, context={"project": project})
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data, status=status.HTTP_201_CREATED, safe=False)
        else:
            return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        data = JSONParser().parse(request)
        serializer = ProjectMemberRemoveSerializer(data=data, context={"project": project})
        if serializer.is_valid():
            serializer.save()
            return JsonResponse({}, status=status.HTTP_204_NO_CONTENT)
        else:
            return JsonResponse({serializer.errors}, status=status.HTTP_400_BAD_REQUEST)