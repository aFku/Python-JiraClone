from django.db import models
from django.core.validators import MinLengthValidator

class Project(models.Model):
    id = models.CharField(max_length=3, primary_key=True, validators=[MinLengthValidator(3)])
    project_name = models.CharField(max_length=25, blank=False, validators=[MinLengthValidator(3)])
    last_task_index = models.PositiveIntegerField(default=0)

    # sprints - Sprint model. 1 Project have many sprints. 1 Sprint have 1 Project
    # tasks - Task model. 1 Project have many tasks. 1 Task have 1 project
    # members - User profile model. Many users have access to many projects
    # chat_observers - User profile model. Many users have observes many chats

    def get_members(self, role=None):
        if role:
            return ProjectMember.objects.filter(project=self, role=role)
        else:
            return ProjectMember.objects.filter(project=self)

    def role_by_user_id(self, user_id: str):
        try:
            return ProjectMember.objects.get(project=self, user_id=user_id).role
        except models.ObjectDoesNotExist:
            return None

    def add_member(self, user_id: str, role):
        return ProjectMember.objects.get_or_create(project=self, user_id=user_id, role=role)

    def remove_member(self, user_id: str):
        ProjectMember.objects.filter(project=self, user_id=user_id).delete()

class ProjectMember(models.Model):
    id = models.AutoField(primary_key=True)
    user_id = models.CharField() # supplied by request, userID not stored in this project
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='members')

    class Role(models.TextChoices):
        VIEWER = 'Viewer'
        DEVELOPER = 'Developer'
        ADMIN = 'Admin'

    role = models.CharField(choices=Role.choices,
                              default=Role.DEVELOPER,
                              blank=False)

    def get_role(self) -> Role:
        return self.Role(self.role)