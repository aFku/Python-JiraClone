from django.db import models
from django.core.validators import MinLengthValidator
from django.utils import timezone

class Sprint(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=32, validators=[MinLengthValidator(3)], blank=False)
    start_date = models.DateTimeField(null=True)
    close_date = models.DateTimeField(null=True)
    project = models.ForeignKey('projects_app.Project', on_delete=models.CASCADE, null=False, related_name='sprints')

    class SprintStatus(models.TextChoices):
        CREATED = 'Created', 'Created'
        STARTED = 'Started', 'Started'
        CLOSED = 'Closed',  'Closed'

    status = models.CharField(choices=SprintStatus.choices,
                              default=SprintStatus.CREATED,
                              blank=False)

    def get_status(self) -> SprintStatus:
        return self.SprintStatus(self.status)

    class InvalidSprintStatusTransition(Exception):
        pass

    def start_sprint(self):
        if self.status == self.SprintStatus.CREATED:
            self.start_date = timezone.now()
            self.close_date = None
            self.save()
            return
        raise self.InvalidSprintStatusTransition()

    def close_sprint(self):
        if self.status == self.SprintStatus.STARTED:
            self.close_date = timezone.now()
            self.save()
            return
        raise self.InvalidSprintStatusTransition()


    # tasks - Task model. Many-to-Many.