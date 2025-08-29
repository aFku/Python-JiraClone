from django.db import models

class Project(models.Model):
    id = models.CharField(max_length=3, primary_key=True)
    project_name = models.CharField(max_length=25, blank=False)


    # sprints - Sprint model. 1 Project have many sprints. 1 Sprint have 1 Project
    # tasks - Task model. 1 Project have many tasks. 1 Task have 1 project
    # users_with_access - User profile model. Many users have access to many projects
    # chat_observers - User profile model. Many users have observes many chats
