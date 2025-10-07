from django.urls import path, include

from .views import TasksView, TaskByIdView, CommentByIdView, CommentListCreateView, TaskObserversView

urlpatterns = [
    path('', TasksView.as_view()),
    path('<str:task_pk>/', TaskByIdView.as_view()),
    path('<str:task_pk>/comments/', CommentListCreateView.as_view()),
    path('<str:task_pk>/observers/', TaskObserversView.as_view()),
    path('comments/<int:comment_pk>/', CommentByIdView.as_view()),
]