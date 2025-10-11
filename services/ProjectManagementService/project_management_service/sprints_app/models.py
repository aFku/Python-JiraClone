from django.db import models
from django.core.validators import MinLengthValidator
from .services.sprint_status_management import SprintStatus
from utils.models_helpers import ProjectRelated

class Sprint(models.Model, ProjectRelated):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=32, validators=[MinLengthValidator(3)], blank=False)
    start_date = models.DateTimeField(null=True)
    close_date = models.DateTimeField(null=True)
    project = models.ForeignKey('projects_app.Project', on_delete=models.CASCADE, null=False, related_name='sprints')

    status = models.CharField(choices=SprintStatus.choices,
                              default=SprintStatus.CREATED,
                              blank=False)

    def get_status(self) -> SprintStatus:
        return SprintStatus(self.status)

    def get_project(self):
        return self.project
    # tasks - Task model. Many-to-Many.