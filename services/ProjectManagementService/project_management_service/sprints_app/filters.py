import django_filters

from .models import Sprint

class SprintFilter(django_filters.FilterSet):

    start_date_after = django_filters.IsoDateTimeFilter(
        field_name="start_date", lookup_expr="gte"
    )
    start_date_before = django_filters.IsoDateTimeFilter(
        field_name="start_date", lookup_expr="lte"
    )
    close_date_after = django_filters.IsoDateTimeFilter(
        field_name="close_date", lookup_expr="gte"
    )
    close_date_before = django_filters.IsoDateTimeFilter(
        field_name="close_date", lookup_expr="lte"
    )

    class Meta:
        model = Sprint
        fields = ['project', 'status', 'start_date', 'close_date']