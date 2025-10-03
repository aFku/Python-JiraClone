from django.urls import path, include

from .views import ProjectsView, project_by_id, project_members

urlpatterns = [
    path('', ProjectsView.as_view()),
    path('<str:project_pk>/', project_by_id),
    path('<str:project_pk>/members/', project_members)
]