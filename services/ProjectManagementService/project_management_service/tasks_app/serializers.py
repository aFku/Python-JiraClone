from rest_framework import serializers

from .models import Task
from .services.task_management.task_status_workflow import Status, IncorrectTaskTransition
from .services.task_management.task_relationship import IncorrectTaskRelationship
from projects_app.models import Project

class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ['id', 'summary', 'description', 'assignee', 'creator', 'due_date', 'creation_date', 'close_date',
                  'last_edit_time', 'parent', 'sprint', 'project', 'estimate', 'type', 'priority', 'status']

class TaskCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ['summary', 'description', 'assignee', 'due_date', 'parent', 'sprint', 'project', 'estimate',
                  'type', 'priority', 'creator']

        extra_kwargs = {
            "summary": {"required": True},
            "project": {"required": True},
            "type": {"required": True},
            "description": {"required": False, "allow_blank": True},
            "assignee": {"required": False, "allow_blank": True},
            "due_date": {"required": False, "allow_null": True},
            "parent": {"required": False, "allow_null": True},
            "sprint": {"required": False, "allow_null": True},
            "estimate": {"required": False, "allow_null": True},
            "priority": {"required": False, "allow_null": True},
            "creator": {"read_only": True}
        }

    def create(self, validated_data):
        error = {
            "errors": {}
        }
        user_id = self.context.get("user_id")
        # if request and request.user.is_authenticated:
        #     validated_data['creator'] = request.user
        if user_id:
            validated_data['creator'] = user_id

        project = validated_data.pop('project', None)
        if not project:
            error["errors"]['project'] = ["Field 'project is required"]

        if error["errors"]:
            raise serializers.ValidationError(error)

        return Task.create_for_project(project=project, **validated_data)

class TaskUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Task
        fields = ['summary', 'description', 'assignee', 'due_date', 'parent', 'sprint',
                  'estimate', 'priority', 'status']

    def update(self, instance, validated_data):
        error = {
            "errors": {}
        }
        status = validated_data.pop('status', None)

        if status:
            try:
                instance.change_status(Status(status))
            except IncorrectTaskTransition as e:
                error["errors"]['status'] = [str(e)]

        if 'parent' in validated_data:
            try:
                if validated_data['parent']:
                    project = Project.objects.get(pk=validated_data['parent'])
                    instance.add_parent(project)
                else:
                    instance.remove_parent()
            except Project.DoesNotExist:
                error["errors"]['parent'] = [f'Project {validated_data["parent"]} does not exist']
            except IncorrectTaskRelationship as e:
                error["errors"]['parent'] = [str(e)]

        if error["errors"]:
            raise serializers.ValidationError(error)

        return super().update(instance, validated_data)


