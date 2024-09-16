import django_filters
from django_filters import rest_framework as filters
from django.contrib.auth import get_user_model
from account.models import User,  Trainee, Preference, Staff


User = get_user_model()


class UserFilter(filters.FilterSet):
    date_joined = django_filters.DateFromToRangeFilter()
    first_name = django_filters.CharFilter(field_name='first_name', lookup_expr='iexact')
    phone_number = django_filters.CharFilter(field_name='phone_number', lookup_expr='iexact')

    class Meta:
        model = User
        fields = ['date_joined', 'first_name', 'phone_number']

class TraineeFilter(filters.FilterSet):
    date_joined = django_filters.DateFromToRangeFilter()
    first_name = django_filters.CharFilter(field_name='first_name', lookup_expr='iexact')
    phone_number = django_filters.CharFilter(field_name='phone_number', lookup_expr='iexact')
    
class Meta:
        model = Trainee
        fields = ['date_joined', 'first_name', 'phone_number']
        
class StaffFilter(filters.FilterSet):
    date_joined = django_filters.DateFromToRangeFilter()
    first_name = django_filters.CharFilter(field_name='first_name', lookup_expr='iexact')
    phone_number = django_filters.CharFilter(field_name='phone_number', lookup_expr='iexact')
    

    class Meta:
        model = Staff
        fields = ['date_joined', 'first_name', 'phone_number']


class PreferenceFilter(django_filters.FilterSet):
    language = django_filters.CharFilter(field_name='language', lookup_expr='iexact')
    bank = django_filters.CharFilter(field_name='bank__bank_name', lookup_expr='iexact')


    class Meta:
        model = Preference
        fields = ['language', 'bank']