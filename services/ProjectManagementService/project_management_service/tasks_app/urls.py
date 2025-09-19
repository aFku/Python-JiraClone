from django.urls import path, include

from .views import tasks_view, tasks_by_id_view, comments_by_task, comment_by_id, task_observers

urlpatterns = [
    path('', tasks_view),
    path('<str:task_pk>/', tasks_by_id_view),
    path('<str:task_pk/comments/', comments_by_task),
    path('<str:task_pk>/observers/', task_observers),
    path('comments/<int:comment_pk>/', comment_by_id),
]