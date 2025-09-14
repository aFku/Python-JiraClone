from django.urls import path, include

from .views import projects, project_by_id, project_members

urlpatterns = [
    path('', projects),
    path('<str:pk>/', project_by_id),
    path('<str:pk>/members/', project_members)
]