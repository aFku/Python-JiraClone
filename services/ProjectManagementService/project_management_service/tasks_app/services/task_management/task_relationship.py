from django.db import models


class TaskType(models.TextChoices):
    SUBTASK = 'Subtask', 'Subtask'
    TASK = 'Task', 'Task'
    EPIC = 'Epic', 'Epic'
    INITIATIVE = 'Initiative', 'Initiative'
    BUG = 'Bug', 'Bug'
    SUPPORT = 'Support', 'Support'


class IncorrectTaskRelationship(Exception):
    pass


class TaskRelationship:

    possible_children = {
        TaskType.SUBTASK: (),
        TaskType.TASK: (
            TaskType.SUBTASK
        ),
        TaskType.BUG: (
            TaskType.SUBTASK
        ),
        TaskType.SUPPORT: (
            TaskType.SUBTASK
        ),
        TaskType.EPIC: (
            TaskType.TASK,
            TaskType.BUG,
            TaskType.SUPPORT
        ),
        TaskType.INITIATIVE: (
            TaskType.EPIC
        )
    }

    @classmethod
    def can_be_related(cls, parent_type: TaskType, child_type: TaskType) -> bool:
        return child_type in cls.possible_children[parent_type]