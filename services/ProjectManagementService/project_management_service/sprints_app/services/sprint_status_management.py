from django.db import models
from django.utils import timezone

class SprintStatus(models.TextChoices):
    CREATED = 'Created', 'Created'
    STARTED = 'Started', 'Started'
    CLOSED = 'Closed', 'Closed'

class InvalidSprintStatusTransition(Exception):
    pass

class SprintStatusManager:

    @classmethod
    def start_sprint(cls, sprint):
        if sprint.status == SprintStatus.CREATED:
            sprint.start_date = timezone.now()
            sprint.close_date = None
            return
        raise InvalidSprintStatusTransition(f'Sprint ID: {sprint.id} - Cannot start sprint when it has status: "{sprint.status}"')

    @classmethod
    def close_sprint(cls, sprint):
        if sprint.status == SprintStatus.STARTED:
            sprint.close_date = timezone.now()
            return
        raise InvalidSprintStatusTransition(f'Sprint ID: {sprint.id} - Cannot close sprint when it has status: "{sprint.status}"')

    @classmethod
    def change_status(cls, to_status: SprintStatus, sprint):
        if to_status == SprintStatus.STARTED:
            cls.start_sprint(sprint)
        elif to_status == SprintStatus.CLOSED:
            cls.close_sprint(sprint)
        else:
            raise InvalidSprintStatusTransition(
                f'Sprint ID: {sprint.id} - Cannot move sprint to status: "{to_status}"')