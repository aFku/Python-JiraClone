from django.db import models, transaction

from ..sprints_app.models import Sprint
from ..projects_app.models import Project

class Task(models.Model):
    #id =
    summary = models.CharField(max_length=100, blank=False)
    description = models.CharField(max_length=255)

    assignee = models.CharField(blank=True) # supplied by request, userID not stored in this project
    creator = models.CharField(blank=False) # supplied by request, userID not stored in this project

    due_date = models.DateTimeField(null=True)
    creation_date = models.DateTimeField(auto_now_add=True)
    close_date = models.DateTimeField(null=True)
    last_edit_time = models.DateTimeField(auto_now=True)

    parent = models.ForeignKey('self', on_delete=models.SET_NULL)
    sprint = models.ManyToManyRel(Sprint, related_name='tasks')
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    estimate = models.IntegerField(null=True)

    class TaskType(models.TextChoices):
        TASK = 'Task'
        EPIC = 'Epic'
        INITIATIVE = 'Initiative'
        BUG = 'Bug'
        SUPPORT = 'Support'

    type = models.CharField(choices=TaskType.choices,
                              default=TaskType.TASK,
                              blank=False)

    def get_type(self) -> TaskType:
        return self.TaskType(self.type)

    class Priority(models.TextChoices):
        URGENT = 'Urgent'
        HIGH = 'High'
        MEDIUM = 'Medium'
        LOW = 'Low'

    priority = models.CharField(choices=Priority.choices,
                              default=Priority.MEDIUM,
                              blank=False)

    def get_priority(self) -> Priority:
        return self.Priority(self.priority)

    class Status(models.TextChoices):
        TO_DO = 'To Do'
        IN_PROGRESS = 'In Progress'
        IN_REVIEW = 'In Review'
        CLOSED = 'Closed'

    status = models.CharField(choices=Status.choices,
                              default=Status.TO_DO,
                              blank=False)

    def get_status(self) -> Status:
        return self.Status(self.status)

    # Observers
    def add_observer(self, user_id: str):
        return TaskObservers.objects.get_or_create(task=self, user_id=user_id)

    def remove_watcher(self, user_id: str):
        TaskObservers.objects.filter(task=self, user_id=user_id).delete()

    def is_watched_by(self, user_id: str):
        return TaskObservers.objects.filter(task=self, user_id=user_id).exists

    @classmethod
    def create_for_project(cls, project: Project, **kwargs):
        with transaction.atomic():
            project_locked = Project.objects.select_for_update().get(pk=project.pk)
            project_locked.last_task_number += 1
            project_locked.save(update_fields=['last_task_number'])
            project_locked.refresh_from_db(fields=['last_task_number'])
            new_number = project_locked.last_task_number
            task_id = f"{str(project_locked.id)}-{new_number}"
            return cls.objects.create(
                id=task_id,
                project=project_locked,
                number=new_number,
                **kwargs
            )

    # TO DO - Move task between projects


class TaskObservers(models.Model):
    id = models.AutoField(primary_key=True)
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    userID = models.CharField(max_length=64, blank=False)


class Comment(models.Model):
    id = models.AutoField(primary_key=True)
    author = models.CharField(max_length=64, blank=False)
    content = models.CharField(max_length=255)
    creation_date = models.DateTimeField(auto_now_add=True)
    last_edit_time = models.DateTimeField(auto_now=True)

