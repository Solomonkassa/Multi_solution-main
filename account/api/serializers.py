from rest_framework import serializers
from account.models import Trainee, User, Preference, OTP, Staff
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.hashers import make_password
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from django.conf import settings
import random

User = get_user_model()


class TraineeSerializer(serializers.ModelSerializer):
    """
    Serializer for Trainee model.
    """
    bank_name = serializers.CharField(source='account_options.bank_name', read_only=True)
    training_type = serializers.CharField(source='training.training', read_only=True)

    class Meta:
        model = Trainee
        fields = (
            "id", "first_name", "middle_name", "last_name", "phone_number",
            "training" ,"training_type","account_options","trans_num","bank_name", "trans_num", "email", "gender",
            "country", "city", "register_date", "is_phone_verified"
        )
        extra_kwargs = {
            "first_name": {"required": True, "allow_blank": False},
            "last_name": {"required": True, "allow_blank": False},
        }
        
class LoginSerializer(serializers.Serializer):
    phone_number = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        phone_number = data.get('phone_number')
        password = data.get('password')

        if phone_number and password:
            try:
                user = User.objects.get(phone_number=phone_number)
            except User.DoesNotExist:
                raise serializers.ValidationError("Invalid phone number or password.")
            
            if not user.check_password(password):
                raise serializers.ValidationError("Invalid phone number or password.")
        else:
            raise serializers.ValidationError("Must include 'phone_number' and 'password'.")

        data['user'] = user
        return data

    def get_tokens(self, user):
        refresh = RefreshToken.for_user(user)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }
        


class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        try:
            user = User.objects.get(email=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("User with this email does not exist.")
        return value

    def save(self):
        email = self.validated_data['email']
        user = User.objects.get(email=email)
        otp = str(random.randint(1000, 9999))
        get_user = get_object_or_404(User, email=email)
        
        # Save OTP to the database
        OTP.objects.create(user=user, otp=otp)
        
        subject = 'Multi Solutions OTP Verification'
        message = f'Dear {get_user.first_name},\n\nThank you for choosing Multi Solutions.\n\nYour One-Time Password (OTP) for verification is: {otp}\n\nPlease enter this OTP on the provided platform to complete the verification process.\n\nIf you did not request this OTP, please disregard this message.\n\nBest Regards,\nMulit Solutions Team'
        
        # Send OTP via email
        send_mail(
            subject,
            message,
            settings.EMAIL_HOST_USER,
            [email], 
            fail_silently=False,
        )

class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)
    new_password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        try:
            user = User.objects.get(email=attrs['email'])
            otp_instance = OTP.objects.filter(user=user, otp=attrs['otp']).last()
            if not otp_instance or not otp_instance.is_valid():
                raise serializers.ValidationError("Invalid or expired OTP.")
        except User.DoesNotExist:
            raise serializers.ValidationError("User with this email does not exist.")
        return attrs

    def save(self):
        user = User.objects.get(email=self.validated_data['email'])
        user.set_password(self.validated_data['new_password'])
        user.save()
        OTP.objects.filter(user=user).delete()  # Clear OTPs after successful reset


class VerifyOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)

    def validate(self, attrs):
        try:
            user = User.objects.get(email=attrs['email'])
            otp_instance = OTP.objects.filter(user=user, otp=attrs['otp']).last()
            if not otp_instance or not otp_instance.is_valid():
                raise serializers.ValidationError("Invalid or expired OTP.")
        except User.DoesNotExist:
            raise serializers.ValidationError("User with this email does not exist.")
        return attrs
     
class CustomUserSerializer(serializers.ModelSerializer):
    """
    Serializer for User model.
    """
    bank_name = serializers.CharField(source='account_options.bank_name', read_only=True)
    training_type = serializers.CharField(source='training.training', read_only=True)
    password = serializers.CharField(write_only=True, style={"input_type": "password"})

    class Meta:
        model = User
        fields = (
            "id", "first_name", "middle_name", "last_name", "phone_number",
            "training", "training_type", "account_options", "bank_name", "trans_num", "email", "gender",
            "country", "city", "register_date", "is_superuser", "is_staff", "is_active", "is_phone_verified", "last_login", "date_joined", "is_phone_verified", "is_trainee", "password",
        )
        extra_kwargs = {
            "first_name": {"required": True, "allow_blank": False},
            "last_name": {"required": True, "allow_blank": False},
        }

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        if password:
            instance.password = make_password(password)
        return super().update(instance, validated_data)
    

class StaffSerializer(serializers.ModelSerializer):
    """
    Serializer for Staff model.
    """
    password = serializers.CharField(write_only=True, style={"input_type": "password"})

    class Meta:
        model = Staff
        fields = (
            "id", "first_name", "middle_name", "last_name", "phone_number",
            "email", "gender", "country", "city", "register_date", "is_superuser",
            "is_staff", "is_active", "is_phone_verified", "last_login", "date_joined", "is_phone_verified", "password",
        )
        extra_kwargs = {
            "first_name": {"required": True, "allow_blank": False},
            "last_name": {"required": True, "allow_blank": False},
        }

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        if password:
            instance.password = make_password(password)
        return super().update(instance, validated_data)



class PreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Preference
        fields = '__all__'
