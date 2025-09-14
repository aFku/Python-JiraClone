from django.urls import path, include

from .views import sprints_view, sprint_by_id_view

urlpatterns = [
    path('', sprints_view),
    path('<int:pk>/', sprint_by_id_view)
]