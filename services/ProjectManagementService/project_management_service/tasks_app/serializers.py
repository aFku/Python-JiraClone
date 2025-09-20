from rest_framework import serializers

from .models import Task, Comment, TaskObserver
from .services.task_management.task_status_workflow import Status, IncorrectTaskTransition
from .services.task_management.task_relationship import IncorrectTaskRelationship
from .services.task_management.task_sprint_manager import TaskSprintManagement
from projects_app.models import Project
from sprints_app.models import Sprint

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

        sprints = validated_data.pop('sprint', [])

        if error["errors"]:
            raise serializers.ValidationError(error)

        task = Task.create_for_project(project=project, **validated_data)
        for sprint in sprints:
            TaskSprintManagement.add_task_to_sprint(task, sprint)
        return task


class TaskUpdateSerializer(serializers.ModelSerializer):
    add_sprint = serializers.PrimaryKeyRelatedField(
        queryset=Sprint.objects.all(), required=False, write_only=True, many=True
    )
    remove_sprint = serializers.PrimaryKeyRelatedField(
        queryset=Sprint.objects.all(), required=False, write_only=True, many=True
    )

    class Meta:
        model = Task
        fields = ['summary', 'description', 'assignee', 'due_date', 'parent', 'add_sprint', 'remove_sprint',
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

        add_sprints = validated_data.pop('add_sprint', [])
        remove_sprints = validated_data.pop('remove_sprint', [])

        for sprint in add_sprints:
            try:
                TaskSprintManagement.add_task_to_sprint(instance, sprint)
            except serializers.ValidationError as e:
                error["errors"].setdefault('add_sprint', []).append(str(e.detail[0]))

        for sprint in remove_sprints:
            try:
                TaskSprintManagement.remove_task_from_sprint(instance, sprint)
            except serializers.ValidationError as e:
                error["errors"].setdefault('remove_sprint', []).append(str(e.detail[0]))

        if error["errors"]:
            raise serializers.ValidationError(error)

        return super().update(instance, validated_data)


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['id', 'task', 'author', 'content', 'creation_date', 'last_edit_time']


class CommentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['task', 'author', 'content']

        extra_kwargs = {
            "author": {"read_only": True},
            "task": {"read_only": True}
        }

    def create(self, validated_data):
        internal_data = {
            "author": self.context.get("user_id"),
            "task": self.context.get("task")
        }
        validated_data.update(internal_data)

        return super().create(validated_data)


class CommentUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['content']


class TaskObserverSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskObserver
        fields = ['task', 'user_id']

        extra_kwargs = {
            "user_id": {"read_only": True},
            "task": {"read_only": True}
        }

    def create(self, validated_data):
        internal_data = {
            "user_id": self.context.get("user_id"),
            "task": self.context.get("task")
        }
        validated_data.update(internal_data)
        return super().create(internal_data)
