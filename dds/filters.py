import django_filters

from .models import Operation, Category, Subcategory, OperationStatus, OperationType


class OperationFilter(django_filters.FilterSet):
    date_from = django_filters.DateFilter(field_name='date', lookup_expr='gte')
    date_to = django_filters.DateFilter(field_name='date', lookup_expr='lte')
    status = django_filters.ModelChoiceFilter(queryset=OperationStatus.objects.all())
    type = django_filters.ModelChoiceFilter(field_name='type', queryset=OperationType.objects.all())
    category = django_filters.ModelChoiceFilter(queryset=Category.objects.all())
    subcategory = django_filters.ModelChoiceFilter(queryset=Subcategory.objects.all())

    class Meta:
        model = Operation
        fields = ['date_from', 'date_to', 'status', 'type', 'category', 'subcategory']
