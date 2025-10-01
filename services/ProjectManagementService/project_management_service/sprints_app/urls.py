from django.urls import path, include

from .views import SprintsView, SprintByIdView

urlpatterns = [
    path('', SprintsView.as_view()),
    path('<int:sprint_pk>/', SprintByIdView.as_view())
]