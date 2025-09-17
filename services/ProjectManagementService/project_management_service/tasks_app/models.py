from django.db import models, transaction
from django.utils import timezone

from .services.task_management.task_status_workflow import TaskStatusWorkFlow, IncorrectTaskTransition, Status
from .services.task_management.task_relationship import TaskType, IncorrectTaskRelationship, TaskRelationship

class Task(models.Model):
    id = models.CharField(max_length=64, primary_key=True)
    number = models.IntegerField(null=False)

    summary = models.CharField(max_length=100)
    description = models.CharField(max_length=255, blank=True)

    assignee = models.CharField(max_length=64, blank=True, null=True)
    creator = models.CharField(max_length=64, blank=False)

    due_date = models.DateTimeField(null=True, blank=True)
    creation_date = models.DateTimeField(auto_now_add=True)
    close_date = models.DateTimeField(null=True, blank=True)
    last_edit_time = models.DateTimeField(auto_now=True)

    parent = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='children')
    sprint = models.ManyToManyField('sprints_app.Sprint', related_name='tasks', blank=True)
    project = models.ForeignKey('projects_app.Project', on_delete=models.CASCADE, related_name='tasks')

    estimate = models.IntegerField(null=True, blank=True)


    type = models.CharField(max_length=20, choices=TaskType.choices, default=TaskType.TASK)

    class Priority(models.TextChoices):
        URGENT = 'Urgent', 'Urgent'
        HIGH = 'High', 'High'
        MEDIUM = 'Medium', 'Medium'
        LOW = 'Low', 'Low'

    priority = models.CharField(max_length=10, choices=Priority.choices, default=Priority.MEDIUM)

    status = models.CharField(max_length=20, choices=Status.choices, default=Status.TO_DO)

    class ProjectRequiredException(Exception):
        pass

    def get_type(self) -> TaskType:
        return TaskType(self.type)

    def get_priority(self) -> Priority:
        return self.Priority(self.priority)

    def get_status(self) -> Status:
        return Status(self.status)

    # Observers
    def add_observer(self, user_id: str):
        obj, created = TaskObserver.objects.get_or_create(task=self, user_id=user_id)
        return obj, created

    def remove_observer(self, user_id: str):
        TaskObserver.objects.filter(task=self, user_id=user_id).delete()

    def is_watched_by(self, user_id: str) -> bool:
        return TaskObserver.objects.filter(task=self, user_id=user_id).exists()

    @classmethod
    def create_for_project(cls, project, **kwargs):
        if project is None:
            raise cls.ProjectRequiredException()
        with transaction.atomic():
            project_locked = project.__class__.objects.select_for_update().get(pk=project.pk)
            project_locked.last_task_index = (project_locked.last_task_index or 0) + 1
            project_locked.save(update_fields=['last_task_index'])
            new_number = project_locked.last_task_index
            task_id = f"{str(project_locked.id)}-{new_number}"
            return cls.objects.create(
                id=task_id,
                project=project_locked,
                number=new_number,
                **kwargs
            )

    def add_parent(self, parent: "Task"):
        if self.parent is not None:
            self.remove_parent()

        if not TaskRelationship.can_be_related(parent.get_type(), self.get_type()):
            raise IncorrectTaskRelationship(f'Task ID: {self.id} (type: {self.get_type()}) - Cannot add parent with id "{parent.id}" (type: "{parent.get_type()}")')

        self.parent = parent

    def remove_parent(self):
        if self.parent is not None:
            self.parent = None

    def change_status(self, to_status: Status):
        if not TaskStatusWorkFlow.can_transition(self.get_status(), to_status):
            raise IncorrectTaskTransition(f'Task ID: {self.id} - Cannot change status from "{self.status}" to "{to_status}"')


        self.status = to_status

    def save(
        self,
        *args,
        force_insert=False,
        force_update=False,
        using=None,
        update_fields=None,
    ):
        self.last_edit_time = timezone.now()
        super().save(*args,
                     force_insert=force_insert,
                     force_update=force_update,
                     using=using,
                     update_fields=update_fields
                     )

    def __str__(self):
        return f"{self.id} - {self.summary}"


class TaskObserver(models.Model):
    id = models.AutoField(primary_key=True)
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='observers')
    user_id = models.CharField(max_length=64)


class Comment(models.Model):
    id = models.AutoField(primary_key=True)
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='comments', null=False)
    author = models.CharField(max_length=64)
    content = models.CharField(max_length=255)
    creation_date = models.DateTimeField(auto_now_add=True)
    last_edit_time = models.DateTimeField(auto_now=True)

    def save(
        self,
        *args,
        force_insert=False,
        force_update=False,
        using=None,
        update_fields=None,
    ):
        self.last_edit_time = timezone.now()
        super().save(*args,
                     force_insert=force_insert,
                     force_update=force_update,
                     using=using,
                     update_fields=update_fields
                     )

    def __str__(self):
        return f"Comment by {self.author} on {self.creation_date}"