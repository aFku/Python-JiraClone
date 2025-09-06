from django.db import models


class Status(models.TextChoices):
    TO_DO = 'To Do', 'To Do'
    IN_PROGRESS = 'In Progress', 'In Progress'
    IN_REVIEW = 'In Review', 'In Review'
    CLOSED = 'Closed', 'Closed'


class IncorrectTaskTransition(Exception):
    pass


class TaskStatusWorkFlow:

    transitions = {
        Status.TO_DO: (
            Status.IN_PROGRESS,
            Status.CLOSED
        ),
        Status.IN_PROGRESS: (
            Status.TO_DO,
            Status.IN_REVIEW,
            Status.CLOSED
        ),
        Status.IN_REVIEW: (
            Status.TO_DO,
            Status.IN_PROGRESS,
            Status.CLOSED
        ),
        Status.CLOSED: (
            Status.TO_DO,
            Status.IN_PROGRESS
        )
    }

    @classmethod
    def can_transition(cls, from_status: Status, to_status: Status) -> bool:
        return to_status in cls.transitions[from_status]
