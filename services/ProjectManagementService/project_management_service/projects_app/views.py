from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser
from rest_framework import status
from rest_framework.decorators import api_view

from .serializers import ProjectSerializer, ProjectMemberSerializer, AddMembersSerializer, ProjectMemberAddResponseSerializer
from .models import Project, ProjectMember


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
def project_by_id(request, pk):
    try:
        project = Project.objects.get(id=pk)
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
def project_members(request, pk):
    try:
        project = Project.objects.get(id=pk)
    except Project.DoesNotExist:
        JsonResponse({"error": "Project not found"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        role_param = request.query_params.get('role', None)
        serializer = ProjectMemberSerializer(project.get_members(role_param), many=True)
        return JsonResponse(serializer.data, safe=False)

    elif request.method == 'POST':
        serializer = AddMembersSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        members_data = serializer.validated_data['members']

        response_data = []

        for m in members_data:
            member, created = ProjectMember.objects.get_or_create(
                project=project,
                user_id=m['user_id'],
                defaults={'role': m['role']}
            )
            if not created:
                member.role = m['role']
                member.save()

            response_data.append({
                "user_id": member.user_id,
                "role": member.role,
                "added": created
            })

        response_serializer = ProjectMemberAddResponseSerializer(response_data, many=True)
        return JsonResponse(response_serializer.data, status=status.HTTP_201_CREATED, safe=False)

    elif request.method == 'DELETE':
        user_id = request.query_params.get('user_id')
        if not user_id:
            return JsonResponse({"error": "user_id query param is required"}, status=status.HTTP_400_BAD_REQUEST)

        deleted, _ = ProjectMember.objects.filter(project=project, user_id=user_id).delete()
        if deleted:
            return JsonResponse({}, status=status.HTTP_204_NO_CONTENT)
        else:
            return JsonResponse({"error": "Member not found"}, status=status.HTTP_404_NOT_FOUND)