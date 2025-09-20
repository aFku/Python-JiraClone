from rest_framework import serializers
from sprints_app.models import Sprint

class TaskSprintManagement:

    @classmethod
    def remove_task_from_sprint(cls, task, sprint):
        if not task.sprint.filter(pk=sprint.pk).exists():
            raise serializers.ValidationError("Task is not included in given sprint")

        if sprint.status == Sprint.SprintStatus.CLOSED:
            raise serializers.ValidationError("Cannot remove task from closed sprint")

        return task.sprint.remove(sprint)

    @classmethod
    def add_task_to_sprint(cls, task, sprint):
        if task.project != sprint.project:
            raise serializers.ValidationError("Task and sprint are in different projects")

        if sprint.status == Sprint.SprintStatus.CLOSED:
            raise serializers.ValidationError("Cannot add task to already closed sprint")

        task.sprint.add(sprint)


