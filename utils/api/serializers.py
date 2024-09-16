from django.utils.translation import gettext as _
from rest_framework import serializers
from utils.models import Contactus


class ContactusSerializer(serializers.ModelSerializer):
    """
    Serializer for Contact model.
    """
    class Meta:
        model = Contactus
        fields = "__all__"



class BadRequest400Serializer(serializers.Serializer):
    """
    Serializer for Bad Request (400) response.
    """
    detail = serializers.CharField(default=_("Bad request"))

class NotFound404Serializer(serializers.Serializer):
    """
    Serializer for Not Found (404) response.
    """
    detail = serializers.CharField(default=_("Not Found"))

class Forbidden403Serializer(serializers.Serializer):
    """
    Serializer for Forbidden (403) response.
    """
    detail = serializers.CharField(default=_("Forbidden"))

class UnAuthorized401Serializer(serializers.Serializer):
    """
    Serializer for Unauthorized (401) response.
    """
    detail = serializers.CharField(default=_("Unauthorized"))
    
class OtpSerializer(serializers.Serializer):
    """
    Serializer for OTP sent successfully response.
    """
    detail = serializers.CharField(default=_("OTP Sent successfully"))

class OTPVerifySerializer(serializers.Serializer):
    """
    Serializer for valid OTP response.
    """
    detail = serializers.CharField(default=_("OTP is valid"))

class OTPNotFound(serializers.Serializer):
    """
    Serializer for invalid OTP response.
    """
    detail = serializers.CharField(default=_("Invalid user OTP"))

