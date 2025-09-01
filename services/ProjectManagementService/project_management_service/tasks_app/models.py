from django.db import models, transaction
from django.utils import timezone

class Task(models.Model):
    id = models.CharField(max_length=64, primary_key=True)
    number = models.IntegerField(null=False)

    summary = models.CharField(max_length=100)
    description = models.CharField(max_length=255, blank=True)

    assignee = models.CharField(max_length=64, blank=True, null=True)
    creator = models.CharField(max_length=64)

    due_date = models.DateTimeField(null=True, blank=True)
    creation_date = models.DateTimeField(auto_now_add=True)
    close_date = models.DateTimeField(null=True, blank=True)
    last_edit_time = models.DateTimeField(auto_now=True)

    parent = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='children')
    sprint = models.ManyToManyField('sprints_app.Sprint', related_name='tasks', blank=True)
    project = models.ForeignKey('projects_app.Project', on_delete=models.CASCADE, related_name='tasks')

    estimate = models.IntegerField(null=True, blank=True)

    class TaskType(models.TextChoices):
        TASK = 'Task', 'Task'
        EPIC = 'Epic', 'Epic'
        INITIATIVE = 'Initiative', 'Initiative'
        BUG = 'Bug', 'Bug'
        SUPPORT = 'Support', 'Support'

    type = models.CharField(max_length=20, choices=TaskType.choices, default=TaskType.TASK)

    class Priority(models.TextChoices):
        URGENT = 'Urgent', 'Urgent'
        HIGH = 'High', 'High'
        MEDIUM = 'Medium', 'Medium'
        LOW = 'Low', 'Low'

    priority = models.CharField(max_length=10, choices=Priority.choices, default=Priority.MEDIUM)

    class Status(models.TextChoices):
        TO_DO = 'To Do', 'To Do'
        IN_PROGRESS = 'In Progress', 'In Progress'
        IN_REVIEW = 'In Review', 'In Review'
        CLOSED = 'Closed', 'Closed'

    status = models.CharField(max_length=20, choices=Status.choices, default=Status.TO_DO)

    def get_type(self) -> TaskType:
        return self.TaskType(self.type)

    def get_priority(self) -> Priority:
        return self.Priority(self.priority)

    def get_status(self) -> Status:
        return self.Status(self.status)

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

    def add_parent(self):
        pass

    def remove_parent(self):
        pass

    def change_status(self):
        pass

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
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='comments')
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