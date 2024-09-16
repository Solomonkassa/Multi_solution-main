from django.shortcuts import render
from rest_framework.permissions import AllowAny, IsAuthenticated
import django_filters
from django_filters import rest_framework as filters
from rest_framework.pagination import PageNumberPagination
from rest_framework import viewsets
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.conf import settings
import jwt
from rest_framework.exceptions import PermissionDenied
from django.contrib.auth import get_user_model

from enrollment.models import Training, Enrollment
from .serializers import TrainingSerializer, EnrollmentSerializer
from .filter import EnrollmentFilter

User = get_user_model()

class EnrollmentPagination(PageNumberPagination):
    """
    Custom pagination class for Enrollment view.
    """
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 1000

    def get_paginated_response(self, data):
        """
        Override to provide custom pagination response format.
        """
        return super().get_paginated_response(data)

    def paginate_queryset(self, queryset, request, view=None):
        """
        Paginate the queryset after ordering by enrollment date.
        """
        if queryset.ordered:
            return super().paginate_queryset(queryset, request, view)

        ordered_queryset = queryset.order_by('-enrollment_date')
        return super().paginate_queryset(ordered_queryset, request, view)

class TrainingViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Training objects.
    """
    queryset = Training.objects.all()
    serializer_class = TrainingSerializer
    authentication_classes = [JWTAuthentication]

    def get_permissions(self):
        """
        Assign permissions based on action.
        """
        if self.action in ['list', 'retrieve']:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    def get_user_from_token(self, access_token):
        """
        Decode the JWT token to retrieve the user.
        """
        try:
            payload = jwt.decode(access_token, settings.SECRET_KEY, algorithms=['HS256'])
            return User.objects.get(id=payload['user_id'])
        except jwt.ExpiredSignatureError:
            raise PermissionDenied({'message': 'Token has expired'})
        except jwt.InvalidTokenError:
            raise PermissionDenied({'message': 'Invalid token'})
        except User.DoesNotExist:
            raise PermissionDenied({'message': 'User does not exist'})

    def perform_authentication(self, request):
        """
        Perform authentication by extracting the user from the access token in cookies.
        """
        if self.action not in ['list', 'retrieve']:
            access_token = request.COOKIES.get('access_token')
            if not access_token:
                raise PermissionDenied({'message': 'Access token is missing'})

            user = self.get_user_from_token(access_token)
            request.user = user

    def create(self, request, *args, **kwargs):
        """
        Override create method to include authentication.
        """
        self.perform_authentication(request)
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        """
        Override update method to include authentication.
        """
        self.perform_authentication(request)
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """
        Override destroy method to include authentication.
        """
        self.perform_authentication(request)
        return super().destroy(request, *args, **kwargs)

class EnrollmentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Enrollment objects.
    """
    pagination_class = EnrollmentPagination
    queryset = Enrollment.objects.all()
    serializer_class = EnrollmentSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = EnrollmentFilter
    authentication_classes = [JWTAuthentication]

    def get_permissions(self):
        """
        Assign permissions based on action.
        """
        if self.action in ['list', 'retrieve']:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    def get_user_from_token(self, access_token):
        """
        Decode the JWT token to retrieve the user.
        """
        try:
            payload = jwt.decode(access_token, settings.SECRET_KEY, algorithms=['HS256'])
            return User.objects.get(id=payload['user_id'])
        except jwt.ExpiredSignatureError:
            raise PermissionDenied({'message': 'Token has expired'})
        except jwt.InvalidTokenError:
            raise PermissionDenied({'message': 'Invalid token'})
        except User.DoesNotExist:
            raise PermissionDenied({'message': 'User does not exist'})

    def perform_authentication(self, request):
        """
        Perform authentication by extracting the user from the access token in cookies.
        """
        access_token = request.COOKIES.get('access_token')
        if not access_token:
            raise PermissionDenied({'message': 'Access token is missing'})

        user = self.get_user_from_token(access_token)
        request.user = user

    def create(self, request, *args, **kwargs):
        """
        Override create method to include authentication.
        """
        self.perform_authentication(request)
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        """
        Override update method to include authentication.
        """
        self.perform_authentication(request)
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """
        Override destroy method to include authentication.
        """
        self.perform_authentication(request)
        return super().destroy(request, *args, **kwargs)
