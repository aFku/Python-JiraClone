from rest_framework import serializers

from .models import Project, ProjectMember


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ['id', 'project_name']


class ProjectMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectMember
        fields = ['user_id', 'role', 'project']

        extra_kwargs = {
            "project": {"read_only": True}
        }

    def create(self, validated_data):
        project = self.context.get("project")
        member, created = ProjectMember.objects.get_or_create(
            project=project,
            user_id=validated_data.get('user_id'),
            defaults={"role": validated_data["role"]} # Use only for creating, not for searching
        )
        print(member, created)
        if not created and member.role != validated_data.get('role'):
            member.role = validated_data.get('role')
            member.save(update_fields=['role'])
        return member


class ProjectMemberRemoveSerializer(serializers.Serializer):
    users = serializers.ListField(child=serializers.CharField())

    def save(self):
        project = self.context.get('project')
        users = self.validated_data.get('users')
        deleted, _ = ProjectMember.objects.filter(project=project, user_id__in=users).delete()
        return deleted
