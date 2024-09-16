
from django.http.response import JsonResponse
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.response import Response
from django.views.decorators.http import require_http_methods
import django_filters
from django_filters import rest_framework as filters
from account.bot import bot
from django.views.decorators.csrf import csrf_exempt
from rest_framework.viewsets import GenericViewSet, ModelViewSet
import json, telebot
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.db import transaction
from django.conf import settings
import jwt
from rest_framework.exceptions import PermissionDenied
from django.contrib.auth import get_user_model
from datetime import datetime, timedelta


import pytz
from django.utils import timezone
from rest_framework import status, generics
from rest_framework.mixins import CreateModelMixin, DestroyModelMixin, ListModelMixin, UpdateModelMixin
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, ModelViewSet
from rest_framework.pagination import PageNumberPagination
from utils.crypto import hmac_sha256
from utils.api.serializers import (
    BadRequest400Serializer,
    Forbidden403Serializer,
    NotFound404Serializer,
    UnAuthorized401Serializer,
)

from account.models import User,  Trainee, Preference, Staff
from .permissions import IsAdmin
from .filter import UserFilter , TraineeFilter, StaffFilter, PreferenceFilter
from .serializers import (LoginSerializer, ForgotPasswordSerializer, ResetPasswordSerializer, 
                          TraineeSerializer, CustomUserSerializer, PreferenceSerializer, StaffSerializer, VerifyOTPSerializer)


tz = pytz.timezone("Africa/Addis_Ababa")


User = get_user_model()

class TraineePagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 1000

    def get_paginated_response(self, data):
        return super().get_paginated_response(data)

    def paginate_queryset(self, queryset, request, view=None):
        if queryset.ordered:
            return super().paginate_queryset(queryset, request, view)

        ordered_queryset = queryset.order_by('-register_date')
        return super().paginate_queryset(ordered_queryset, request, view)
    
class PreferencePagination(PageNumberPagination):
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

@csrf_exempt
def hook(request):

    body = request.body.decode('utf-8')

    if not body:
        return JsonResponse({'error': 'Request body is empty...'})

    body_data = json.loads(body)
    update = telebot.types.Update.de_json(body_data)
    bot.process_new_updates([update])
    return JsonResponse({"status": "200"}, safe=False)

class LoginView(APIView):
    permission_classes = [AllowAny]
    http_method_names = ['post']

    def post(self, request, *args, **kwargs):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']

        # Generate tokens
        tokens = serializer.get_tokens(user)
        access_token = tokens['access']
        refresh_token = tokens['refresh']

        # Set tokens in cookies
        response = Response({"message": "Login successful"}, status=status.HTTP_200_OK)
        response.set_cookie(
            key='access_token',
            value=access_token,
            httponly=True,
            secure=True,  
            samesite='None', 
            max_age=60*60*24
        )
        response.set_cookie(
            key='refresh_token',
            value=refresh_token,
            httponly=True,
            secure=True,  
            samesite='None', 
            max_age=60*60*24*7
        )

        # Set non-HTTP-only cookie
        response.set_cookie(
            key='Authenticate_User',
            value='IsAuthenticated',
            secure=True,  
            samesite='None',  
            max_age=60*60*24
        )

        response["Access-Control-Allow-Credentials"] = "true"
        return response

class ForgotPasswordView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = ForgotPasswordSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"message": "OTP sent to your email."}, status=status.HTTP_200_OK)

class ResetPasswordView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = ResetPasswordSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"message": "Password reset successful."}, status=status.HTTP_200_OK)

class VerifyOTPView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = VerifyOTPSerializer
    def post(self, request, *args, **kwargs):
        serializer = VerifyOTPSerializer(data=request.data)
        if serializer.is_valid():
            return Response({"detail": "OTP verified successfully."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TraineeViewsets(CreateModelMixin, ListModelMixin, UpdateModelMixin, GenericViewSet):
    """
    Viewset for managing Trainee models. Supports creating, listing, and updating Trainees.
    """
    pagination_class = TraineePagination
    serializer_class = TraineeSerializer
    permission_classes = []
    lookup_field = "phone_number"
    queryset = Trainee.objects.all()
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = TraineeFilter

    def get_queryset(self):
        """
        Optionally filters the queryset by 'date_joined' if provided in the request.
        """
        queryset = self.queryset
        date_joined = self.request.GET.get("date_joined")

        if date_joined:
            try:
                date_joined = timezone.datetime.fromtimestamp(int(date_joined), tz=timezone.utc)
                queryset = queryset.filter(date_joined__lte=date_joined)
            except ValueError:
                # Handle the case where the timestamp is invalid
                queryset = queryset.none()

        return queryset

    def create(self, request, *args, **kwargs):
        """
        Custom create method that normalizes the phone number before creating a Trainee.
        """
        mutable_data = request.data.copy()
        mutable_data['phone_number'] = User.normalize_phone(mutable_data['phone_number'])
        # Check uniqueness of trans_num and id
        trans_num = mutable_data.get('trans_num')
        user_id = mutable_data.get('id')
        if trans_num is not None and User.objects.filter(trans_num=trans_num).exists():
            return Response({"Transaction_number": "Transaction number already exists."}, status=status.HTTP_400_BAD_REQUEST)
        elif user_id is not None and User.objects.filter(id=user_id).exists():
            return Response({"id": "User ID already exists."}, status=status.HTTP_400_BAD_REQUEST)
        else:
            serializer = self.get_serializer(data=mutable_data)
            serializer.is_valid(raise_exception=True)
            try:
                # Save the serializer data only if trans_num is unique
                with transaction.atomic():
                    serializer.save()
            except IntegrityError as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def retrieve(self, request, *args, **kwargs):
        """
        Custom retrieve method that retrieves a Trainee by phone number.
        """
        phone_number = kwargs.get(self.lookup_field)
        queryset = self.filter_queryset(self.get_queryset())
        try:
            instance = queryset.get(phone_number=phone_number)
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        except Trainee.DoesNotExist:
            raise NotFound("Trainee not found with the provided phone number.")

    def update(self, request, *args, **kwargs):
        """
        Custom update method that updates a Trainee by phone number.
        """
        phone_number = kwargs.get(self.lookup_field)
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        try:
            self.perform_update(serializer)
            return Response(serializer.data)
        except Trainee.DoesNotExist:
            raise NotFound("Trainee not found with the provided phone number.")


class UserViewsets(ModelViewSet):
    """
    Viewset for User model.
    """
    pagination_class = TraineePagination
    serializer_class = CustomUserSerializer
    permission_classes = []
    lookup_field = "phone_number"
    queryset = User.objects.all()
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = UserFilter

    def get_queryset(self):
        """
        Optionally filters the queryset by 'date_joined' if provided in the request.
        """
        queryset = self.queryset
        date_joined = self.request.GET.get("date_joined")

        if date_joined:
            try:
                date_joined = timezone.datetime.fromtimestamp(int(date_joined), tz=timezone.utc)
                queryset = queryset.filter(date_joined__lte=date_joined)
            except ValueError:
                # Handle the case where the timestamp is invalid
                queryset = queryset.none()

        return queryset

    def create(self, request, *args, **kwargs):
        """
        Custom create method that normalizes the phone number before creating a User.
        """
        mutable_data = request.data.copy()
        mutable_data['phone_number'] = User.normalize_phone(mutable_data['phone_number'])
        # Check uniqueness of trans_num and id
        trans_num = mutable_data.get('trans_num')
        user_id = mutable_data.get('id')
        if trans_num is not None and User.objects.filter(trans_num=trans_num).exists():
            return Response({"Transaction_number": "Transaction number already exists."}, status=status.HTTP_400_BAD_REQUEST)
        elif user_id is not None and User.objects.filter(id=user_id).exists():
            return Response({"id": "User ID already exists."}, status=status.HTTP_400_BAD_REQUEST)
        else:
            serializer = self.get_serializer(data=mutable_data)
            serializer.is_valid(raise_exception=True)
            try:
                # Save the serializer data only if trans_num is unique
                with transaction.atomic():
                    serializer.save()
            except IntegrityError as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def retrieve(self, request, *args, **kwargs):
        """
        Custom retrieve method that retrieves a Trainee by phone number.
        """
        phone_number = kwargs.get(self.lookup_field)
        queryset = self.filter_queryset(self.get_queryset())
        try:
            instance = queryset.get(phone_number=phone_number)
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        except User.DoesNotExist:
            raise NotFound("User not found with the provided phone number.")

    def update(self, request, *args, **kwargs):
        """
        Custom update method that updates a User by phone number.
        """
        phone_number = kwargs.get(self.lookup_field)
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        try:
            self.perform_update(serializer)
            return Response(serializer.data)
        except User.DoesNotExist:
            raise NotFound("User not found with the provided phone number.")
        
class StaffViewsets(ModelViewSet):
    """
    ViewSet for managing Staff objects.
    """
    pagination_class = TraineePagination
    serializer_class = StaffSerializer
    lookup_field = "phone_number"
    queryset = Staff.objects.all()
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = StaffFilter
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

    def get_queryset(self):
        """
        Optionally filters the queryset by 'date_joined' if provided in the request.
        """
        queryset = self.queryset
        date_joined = self.request.GET.get("date_joined")

        if date_joined:
            try:
                date_joined = timezone.datetime.fromtimestamp(int(date_joined), tz=timezone.utc)
                queryset = queryset.filter(date_joined__lte=date_joined)
            except ValueError:
                # Handle the case where the timestamp is invalid
                queryset = queryset.none()

        return queryset

    def create(self, request, *args, **kwargs):
        """
        Custom create method that normalizes the phone number before creating a User.
        """
        self.perform_authentication(request)

        mutable_data = request.data.copy()
        mutable_data['phone_number'] = User.normalize_phone(mutable_data['phone_number'])
        trans_num = mutable_data.get('trans_num')
        user_id = mutable_data.get('id')

        if trans_num is not None and User.objects.filter(trans_num=trans_num).exists():
            return Response({"Transaction_number": "Transaction number already exists."}, status=status.HTTP_400_BAD_REQUEST)
        elif user_id is not None and User.objects.filter(id=user_id).exists():
            return Response({"id": "User ID already exists."}, status=status.HTTP_400_BAD_REQUEST)
        else:
            serializer = self.get_serializer(data=mutable_data)
            serializer.is_valid(raise_exception=True)
            try:
                with transaction.atomic():
                    serializer.save()
            except IntegrityError as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def retrieve(self, request, *args, **kwargs):
        """
        Custom retrieve method that retrieves a Staff by phone number.
        """
        self.perform_authentication(request)

        phone_number = kwargs.get(self.lookup_field)
        queryset = self.filter_queryset(self.get_queryset())
        try:
            instance = queryset.get(phone_number=phone_number)
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        except Staff.DoesNotExist:
            raise NotFound("Staff not found with the provided phone number.")

    def update(self, request, *args, **kwargs):
        """
        Custom update method that updates a Staff by phone number.
        """
        self.perform_authentication(request)

        phone_number = kwargs.get(self.lookup_field)
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        try:
            self.perform_update(serializer)
            return Response(serializer.data)
        except Staff.DoesNotExist:
            raise NotFound("Staff not found with the provided phone number.")

    def destroy(self, request, *args, **kwargs):
        """
        Custom destroy method that deletes a Staff by phone number.
        """
        self.perform_authentication(request)

        phone_number = kwargs.get(self.lookup_field)
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

        
class PreferenceViewSet(ModelViewSet):
    """
    ViewSet for managing Preference objects.
    """
    pagination_class = PreferencePagination
    queryset = Preference.objects.all()
    serializer_class = PreferenceSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = PreferenceFilter
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

TELEGRAM_BOT_WEBHOOK_URL = "https://cb36c33259b7061e406abd9981a6b021.serveo.net/account/web-hook"

webhook_url = f'{TELEGRAM_BOT_WEBHOOK_URL}'
bot.remove_webhook()
bot.set_webhook(url=webhook_url)
