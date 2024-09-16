import logging
from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.core.mail import send_mail
from django.conf import settings
from .serializers import ContactusSerializer
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.permissions import AllowAny
import jwt
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework.exceptions import PermissionDenied, NotFound

User = get_user_model()

# Initialize logger
logger = logging.getLogger(__name__)

class ContactusViewSet(ViewSet):
    """
    Viewset to handle contact form submissions.
    """
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        request_body=ContactusSerializer,
        responses={status.HTTP_201_CREATED: openapi.Response("Contact form submitted successfully.")},
    )
    def create(self, request, *args, **kwargs):
        serializer = ContactusSerializer(data=request.data)
        if serializer.is_valid():
            try:
                # Extract validated data
                validated_data = serializer.validated_data
                first_name = validated_data.get('first_name')
                last_name = validated_data.get('last_name')
                email = validated_data.get('email')
                message = validated_data.get('message')

                # Sending email notification to admin
                subject = 'New Contact Form Submission'
                email_message = f"A new contact form submission has been received.\n\nName: {first_name} {last_name}\nEmail: {email}\nMessage: {message}"
                send_mail(subject, email_message, settings.EMAIL_HOST_USER, [settings.EMAIL_HOST_USER], fail_silently=True)

                # Sending confirmation email to the sender
                confirmation_subject = 'Thank You for Contacting Multi Solution Driving License'
                confirmation_message = f'Dear {first_name} {last_name},\n\nThank you for reaching out to Multi Solution Driving License. Your message has been successfully received, and we sincerely appreciate the time you have taken to contact us.\n\nOur team is diligently reviewing your inquiry, and we will respond to you as promptly as possible. Should you have any urgent concerns, please do not hesitate to contact us directly at {settings.EMAIL_HOST_USER}.\n\nOnce again, we thank you for choosing Multi Solution Driving License for your needs. We look forward to assisting you further.\n\nWarm regards,\nThe Multi Solution Driving License Team'
                send_mail(confirmation_subject, confirmation_message, settings.EMAIL_HOST_USER, [email], fail_silently=True)

                return Response({'detail': 'Contact form submitted successfully. Thank you for contacting us.'}, status=status.HTTP_201_CREATED)
            except Exception as e:
                logger.error(f"Error processing contact form submission: {e}")
                return Response({'detail': 'An unexpected error occurred while processing your request. Please try again later.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class AdminEmailSendingViewSet(ViewSet):
    """
    ViewSet to handle sending emails to specific users by admin.
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'email': openapi.Schema(type=openapi.TYPE_STRING, description='Recipient email', example='user@example.com'),
                'subject': openapi.Schema(type=openapi.TYPE_STRING, description='Email subject', example='Subject here'),
                'message': openapi.Schema(type=openapi.TYPE_STRING, description='Email message', example='Message content here'),
            },
            required=['email', 'message']
        ),
        responses={
            status.HTTP_201_CREATED: openapi.Response("Email sent successfully."),
            status.HTTP_400_BAD_REQUEST: openapi.Response("Email and message are required."),
            status.HTTP_500_INTERNAL_SERVER_ERROR: openapi.Response("Failed to send email. Please try again later."),
        },
    )
    def create(self, request, *args, **kwargs):
        """
        Send an email to a specific user.
        """
        self.perform_authentication(request)
        email = request.data.get('email')
        subject = request.data.get('subject', 'No subject')
        message = request.data.get('message')

        if not email or not message:
            return Response({'detail': 'Email and message are required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            logger.info(f"Attempting to send email to {email}")
            logger.info(f"Email settings: EMAIL_HOST={settings.EMAIL_HOST}, EMAIL_PORT={settings.EMAIL_PORT}, EMAIL_HOST_USER={settings.EMAIL_HOST_USER}")

            send_mail(subject, message, settings.EMAIL_HOST_USER, [email], fail_silently=False)

            logger.info("Email sent successfully.")
            return Response({'detail': 'Email sent successfully.'}, status=status.HTTP_201_CREATED)
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            return Response({'detail': 'Failed to send email. Please try again later.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def perform_authentication(self, request):
        access_token = request.COOKIES.get('access_token')
        if not access_token:
            raise PermissionDenied({'detail': 'Access token is missing'})

        user = self.get_user_from_token(access_token)
        request.user = user

    def get_user_from_token(self, access_token):
        try:
            payload = jwt.decode(access_token, settings.SECRET_KEY, algorithms=['HS256'])
            return User.objects.get(id=payload['user_id'])
        except jwt.ExpiredSignatureError:
            raise PermissionDenied({'detail': 'Token has expired'})
        except jwt.InvalidTokenError:
            raise PermissionDenied({'detail': 'Invalid token'})
        except User.DoesNotExist:
            raise PermissionDenied({'detail': 'User does not exist'})