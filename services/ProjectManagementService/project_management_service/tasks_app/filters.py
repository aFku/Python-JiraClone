import django_filters

from .models import Task, Comment

class TaskFilter(django_filters.FilterSet):
    due_date_after = django_filters.IsoDateTimeFilter(
        field_name="due_date", lookup_expr="gte"
    )
    due_date_before = django_filters.IsoDateTimeFilter(
        field_name="due_date", lookup_expr="lte"
    )
    creation_date_after = django_filters.IsoDateTimeFilter(
        field_name="creation_date", lookup_expr="gte"
    )
    creation_date_before = django_filters.IsoDateTimeFilter(
        field_name="creation_date", lookup_expr="lte"
    )
    close_date_after = django_filters.IsoDateTimeFilter(
        field_name="close_date", lookup_expr="gte"
    )
    close_date_before = django_filters.IsoDateTimeFilter(
        field_name="close_date", lookup_expr="lte"
    )

    class Meta:
        model = Task
        fields = ['assignee', 'creator', 'due_date', 'creation_date', 'close_date', 'parent', 'sprint', 'project',
                  'type', 'priority', 'status']


class CommentFilter(django_filters.FilterSet):
    creation_date_after = django_filters.IsoDateTimeFilter(
        field_name="creation_date", lookup_expr="gte"
    )
    creation_date_before = django_filters.IsoDateTimeFilter(
        field_name="creation_date", lookup_expr="lte"
    )

    class Meta:
        model = Comment
        fields = ['author', 'task', 'creation_date']