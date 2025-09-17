from django.urls import path, include

from .views import tasks_view, tasks_by_id_view

urlpatterns = [
    path('', tasks_view),
    path('<str:pk>/', tasks_by_id_view)
]