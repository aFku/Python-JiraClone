from django.db import models
from django.core.validators import MinLengthValidator


class Sprint(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=32, validators=[MinLengthValidator(3)], blank=False)
    start_date = models.DateTimeField(null=True)
    close_date = models.DateTimeField(null=True)

    class SprintStatus(models.TextChoices):
        CREATED = 'Created', 'Created'
        STARTED = 'Started', 'Started'
        CLOSED = 'Closed',  'Closed'

    status = models.CharField(choices=SprintStatus.choices,
                              default=SprintStatus.CREATED,
                              blank=False)

    def get_status(self) -> SprintStatus:
        return self.SprintStatus(self.status)

    # tasks - Task model. Many-to-Many.