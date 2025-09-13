from rest_framework import serializers

from .models import Project, ProjectMember


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ['id', 'project_name']


class ProjectMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectMember
        fields = ['user_id', 'role']


class AddMembersSerializer(serializers.Serializer):
     members = ProjectMemberSerializer(many=True)


class ProjectMemberAddResponseSerializer(serializers.Serializer):
    user_id = serializers.CharField()
    role = serializers.CharField()
    added = serializers.BooleanField()
