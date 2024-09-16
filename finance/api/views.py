from django.shortcuts import render, get_object_or_404
from rest_framework import viewsets, status, generics
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
import django_filters
from django.db.models import Q
from rest_framework.decorators import action
from django_filters import rest_framework as filters
import jwt
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework.exceptions import PermissionDenied, NotFound
from finance.models import BankAccount, TraineePayment, MonthlyPayment, MonthlyPaymentCycle
from .serializers import BankAccountSerializer, TraineePaymentSerializer, MonthlyPaymentSerializer, MonthlyPaymentCycleSerializer
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.pagination import PageNumberPagination
from account.models import User
from .filter import TraineePaymentFilter, MonthlyPaymentFilter


User = get_user_model()

class PaymentPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 1000

    def get_paginated_response(self, data):
        return super().get_paginated_response(data)

    def paginate_queryset(self, queryset, request, view=None):
        if queryset.ordered:
            return super().paginate_queryset(queryset, request, view)

        ordered_queryset = queryset.order_by('-created_at')
        return super().paginate_queryset(ordered_queryset, request, view)

class BankAccountViewSet(viewsets.ModelViewSet):
    """
    ViewSet for handling BankAccount CRUD operations.
    """
    queryset = BankAccount.objects.all()
    serializer_class = BankAccountSerializer
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
        Custom create method with authentication.
        """
        self.perform_authentication(request)
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        """
        Custom update method with authentication.
        """
        self.perform_authentication(request)
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """
        Custom destroy method with authentication.
        """
        self.perform_authentication(request)
        return super().destroy(request, *args, **kwargs)

class MonthlyPaymentCycleViewSet(viewsets.ModelViewSet):
    """
    ViewSet for handling MonthlyPaymentCycle CRUD operations.
    """
    queryset = MonthlyPaymentCycle.objects.all()
    serializer_class = MonthlyPaymentCycleSerializer
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


class TraineePaymentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for handling TraineePayment CRUD operations.
    """
    pagination_class = PaymentPagination
    queryset = TraineePayment.objects.all()
    serializer_class = TraineePaymentSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = TraineePaymentFilter
    authentication_classes = [JWTAuthentication]

    def get_permissions(self):
        """
        Assign permissions based on action.
        """
        if self.action in ['list', 'retrieve', 'retrieve_by_phone', 'update_by_phone', 'create']:
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
        if self.action not in ['list', 'retrieve', 'retrieve_by_phone', 'create']:
            access_token = request.COOKIES.get('access_token')
            if not access_token:
                raise PermissionDenied({'message': 'Access token is missing'})

            user = self.get_user_from_token(access_token)
            request.user = user

    def retrieve(self, request, *args, **kwargs):
        """
        Retrieve a TraineePayment by ID.
        """
        self.perform_authentication(request)
        identifier = kwargs.get('pk')
        if identifier.isdigit():
            instance = get_object_or_404(TraineePayment, id=identifier)
        else:
            return Response({'detail': 'Invalid ID format'}, status=status.HTTP_400_BAD_REQUEST)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='phone/(?P<phone_number>[^/.]+)')
    def retrieve_by_phone(self, request, phone_number=None):
        """
        Retrieve TraineePayments by phone number.
        """
        self.perform_authentication(request)
        user = get_object_or_404(User, phone_number=phone_number)
        instances = TraineePayment.objects.filter(user=user)
        if not instances.exists():
            return Response({'detail': 'No payments found for this user.'}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.get_serializer(instances, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['put', 'patch'], url_path='phone/(?P<phone_number>[^/.]+)')
    def update_by_phone(self, request, phone_number=None, pk=None):
        """
        Update a TraineePayment by phone number.
        """
        self.perform_authentication(request)
        user = get_object_or_404(User, phone_number=phone_number)
        instance = get_object_or_404(TraineePayment, user=user, id=pk)
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
    
class MonthlyPaymentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for handling MonthlyPayment CRUD operations.
    """
    pagination_class = PaymentPagination
    queryset = MonthlyPayment.objects.all()
    serializer_class = MonthlyPaymentSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = MonthlyPaymentFilter
    authentication_classes = [JWTAuthentication]

    def get_permissions(self):
        """
        Assign permissions based on action.
        """
        if self.action in ['list','retrieve', 'retrieve_by_phone', 'update_by_phone', 'create']:
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
        if self.action not in ['list', 'retrieve', 'retrieve_by_phone', 'create']:
            access_token = request.COOKIES.get('access_token')
            if not access_token:
                raise PermissionDenied({'message': 'Access token is missing'})

            user = self.get_user_from_token(access_token)
            request.user = user

    def retrieve(self, request, *args, **kwargs):
        """
        Retrieve a MonthlyPayment by ID.
        """
        self.perform_authentication(request)
        identifier = kwargs.get('pk')
        if identifier.isdigit():
            instance = get_object_or_404(MonthlyPayment, id=identifier)
        else:
            return Response({'detail': 'Invalid ID format'}, status=status.HTTP_400_BAD_REQUEST)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='phone/(?P<phone_number>[^/.]+)')
    def retrieve_by_phone(self, request, phone_number=None):
        """
        Retrieve MonthlyPayments by phone number.
        """
        self.perform_authentication(request)
        user = get_object_or_404(User, phone_number=phone_number)
        instances = MonthlyPayment.objects.filter(user=user)
        if not instances.exists():
            return Response({'detail': 'No payments found for this user.'}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.get_serializer(instances, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['put', 'patch'], url_path='phone/(?P<phone_number>[^/.]+)')
    def update_by_phone(self, request, phone_number=None, pk=None):
        """
        Update a MonthlyPayment by phone number.
        """
        self.perform_authentication(request)
        user = get_object_or_404(User, phone_number=phone_number)
        instance = get_object_or_404(MonthlyPayment, user=user, id=pk)
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
