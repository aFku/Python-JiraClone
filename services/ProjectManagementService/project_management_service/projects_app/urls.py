from django.urls import path, include

from .views import ProjectsView, ProjectByIdView, ProjectMembersView

urlpatterns = [
    path('', ProjectsView.as_view()),
    path('<str:project_id>/', ProjectByIdView.as_view()),
    path('<str:project_id>/members/', ProjectMembersView.as_view())
]