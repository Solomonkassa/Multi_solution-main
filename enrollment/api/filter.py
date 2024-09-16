import django_filters
from django_filters import rest_framework as filters
from django.contrib.auth import get_user_model
from enrollment.models import Enrollment


User = get_user_model()


class EnrollmentFilter(filters.FilterSet):
    training = django_filters.CharFilter(field_name='training', lookup_expr='iexact')
    enrollment_date = django_filters.DateFromToRangeFilter(field_name='enrollment_date')
    is_complete = django_filters.BooleanFilter(field_name='is_complete')
    
    class Meta:
        model = Enrollment
        fields = ['enrollment_date', 'is_complete', 'training']