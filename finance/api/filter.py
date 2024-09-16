import django_filters
from django_filters import rest_framework as filters
from finance.models import MonthlyPayment, TraineePayment

class TraineePaymentFilter(filters.FilterSet):
    created_at = django_filters.DateFromToRangeFilter(field_name='created_at')
    is_completed = django_filters.BooleanFilter(field_name='is_completed')
    is_rejected = django_filters.BooleanFilter(field_name='is_rejected')

    class Meta:
        model = TraineePayment
        fields = ['created_at', 'is_completed', 'is_rejected']

class MonthlyPaymentFilter(filters.FilterSet):
    created_at = django_filters.DateFromToRangeFilter(field_name='created_at')
    is_completed = django_filters.BooleanFilter(field_name='is_completed')
    is_rejected = django_filters.BooleanFilter(field_name='is_rejected')

    class Meta:
        model = MonthlyPayment
        fields = ['created_at', 'is_completed', 'is_rejected']

