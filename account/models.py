# Import necessary modules and packages
from django.db import models
from django.contrib.auth.validators import ASCIIUsernameValidator
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _
from django.conf import settings
import re
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from datetime import timedelta

# Importing necessary functions and models from other modules
from .managers import UserManager, TraineeManager, StaffManager
from utils.crypto import gen_api_key, hash256
from finance.models import  TraineePayment, BankAccount
from .validators import validate_unique_trans_num

PHONE_REGEX = r"^251(7|9)\d{8}"


class APIKey(models.Model):
    """
    Model to store API keys for authentication purposes.
    """

    name = models.CharField(max_length=255)
    key = models.CharField(max_length=255, unique=True, db_index=True, editable=False)
    suspended = models.BooleanField(default=False)

    def save(self, **kwargs):
        """
        Override save method to generate and hash API key if not provided.
        """
        if not self.key:
            key = gen_api_key()
            self.key = hash256(key)
        super().save(**kwargs)

    @staticmethod
    def verify_key(key):
        """
        Verify API key hash in the database.
        """
        try:
            key = hash256(key)
            APIKey.objects.get(suspended=False, key=key)
            return True
        except APIKey.DoesNotExist:
            return False


class User(AbstractUser):
    """
    Custom User model with additional fields and functionalities.
    """

    tg_id = models.BigIntegerField(null=True)
    chat_id = models.BigIntegerField(null=True)
    phone_validator = RegexValidator(
        regex=PHONE_REGEX,
        message="Invalid phone number: should start with 251 and be followed by either 9 or 7 then 8 digits",
    )
    username = models.CharField(
        _("username"),
        max_length=150,
        unique=True,
        null=True,
        blank=True,
        help_text=_(
            "Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only."
        ),
        validators=[ASCIIUsernameValidator()],
        error_messages={"unique": _("A user with that username already exists."),},
    )
    first_name = models.CharField(max_length=255)
    middle_name = models.CharField(max_length=255, null=True, blank=True)
    last_name = models.CharField(max_length=255)
    phone_number = models.CharField(
        max_length=12,
        unique=True,
        null=False,
        default='',
        validators=[phone_validator],
        help_text="Required. 12-digit character should start with 251 followed by either 9 or 7 then 7 digits",
    )
    email = models.EmailField(
        max_length=255,
        unique=True,
        null=True,
        blank=True,
        help_text="Optional. Email of a user e.g., example@gmail.com",
    )
    is_phone_verified = models.BooleanField(default=False)
    country = models.CharField(max_length=255, null=True, blank=True)
    city = models.CharField(max_length=255, null=True, blank=True)
    gender = models.CharField(
        max_length=1, choices=[("M", "Male"), ("F", "Female")], null=True, blank=True
    )
    account_options = models.ForeignKey(
        settings.BANK_AC,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="enrolled_trainee",
    )
    account_num = models.CharField(
        max_length=20, null=True, blank=True, verbose_name=_("Account Number")
    )
    trans_num = models.CharField(
        max_length=20, unique=True, null=True, blank=False, verbose_name=_("Transaction Number"),
        help_text=_(
            "Required. bank unique transaction number."
        ),
        error_messages={"unique": _("A user with that transaction already exists."),},
        validators=[validate_unique_trans_num],
    )
    register_date = models.DateTimeField(
        default=timezone.now,
        help_text="The date and time of registration.",
    )
    REQUIRED_FIELDS = ["first_name", "last_name"]
    EMAIL_FIELD = "email"
    USERNAME_FIELD = "phone_number"
    objects = UserManager()
    is_reg_complete = models.BooleanField(default=False)
    groups = models.ManyToManyField(Group, related_name="user_groups")
    user_permissions = models.ManyToManyField(
        Permission, related_name="user_permissions"
    )

    is_trainee = models.BooleanField(default=False)

    training = models.ForeignKey(
        "enrollment.Training",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="enrolled_trainee",
    )

    @staticmethod
    def normalize_phone(phone_number):
        # Define regex patterns for various phone number formats
        patterns = [
            r'^0(\d+)$',          
            r'^\+?251(\d+)$',      
            r'^251(\d+)$'          
        ]
        
        # Iterate through patterns and try to match the phone number
        for pattern in patterns:
            match = re.match(pattern, phone_number)
            if match:
                return f"251{match.group(1)}"  
        
        # If no match is found, return None or raise an exception based on requirements
        raise ValueError("Invalid phone number format")


    
    def __str__(self) -> str:
        return self.username if self.username else f"{self.first_name}"

class Trainee(User):
    """
    Proxy model for trainee inheriting from User model.
    """

    objects = TraineeManager()

    class Meta:
        proxy = True
        verbose_name = "Trainee"
        verbose_name_plural = "Trainees"
    
    def _handle_trainee_payment_creation(self):
        """
        Handle creation of trainee payment.
        """
        if self.trans_num:
            if TraineePayment.objects.filter(user=self, user__trans_num=self.trans_num).exists():
                print(f"A payment already exists for user {self}.")
            else:
                try:
                    existing_payment = TraineePayment.objects.get(user=self)
                    print(f"A payment already exists for user {self}. Payment: {existing_payment}")
                except TraineePayment.DoesNotExist:
                    trainee_payment = TraineePayment.objects.create(user=self, amount=12000)
                    print("Trainee payment created:", trainee_payment)
                except TraineePayment.MultipleObjectsReturned:
                    print("Multiple payments exist for this user. Unable to create a new payment.")
        else:
            print("The 'trans_num' attribute is not defined on the User model. Unable to create TraineePayment.")
    
    def create_trainee_preference(self):
        """
        Create or update preference for trainee using tg_id.
        """
        if self.trans_num:
            preference, created = Preference.objects.update_or_create(
                tg_id=self.tg_id,
                contact=self,
                bank=self.account_options
            )
            if created:
                print("A new preference was created.")
            else:
                print("The existing preference was updated.")
        else:
            print("The 'trans_num' attribute is not defined on the User model. Unable to create or update Preference.") 


    def save(self, *args, **kwargs):
        """
        Override save method to mark the user as a trainee and handle trainee payment creation.
        """
        self.is_trainee = True
        self.is_reg_complete = True
        super().save(*args, **kwargs)
        
        if self.trans_num and self.is_trainee:
            self._handle_trainee_payment_creation()
            self.create_trainee_preference()

class Staff(User):
    """
    Proxy model for staff inheriting from User model.
    """

    objects = StaffManager()

    class Meta:
        proxy = True
        verbose_name = "Trainee"
        verbose_name_plural = "Trainees"
        
    def save(self, *args, **kwargs):
        """
        Override save method to mark the user as staff.
        """
        self.is_trainee = True
        self.is_reg_complete = True
        super().save(*args, **kwargs)
        
class OTP(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_valid(self):
        expiration_time = self.created_at + timedelta(minutes=10)  
        return timezone.now() < expiration_time  
   

class Preference(models.Model):
    tg_id = models.BigIntegerField(null=True)
    contact = models.ForeignKey(Trainee, on_delete=models.CASCADE, null=True) 
    language = models.CharField(max_length=255, default="english")
    bank = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

@receiver(post_save, sender=Trainee)
def create_pref(sender, instance, **kwargs):
     if kwargs.get("created"):
         Preference.objects.create(contact=instance, tg_id=instance.tg_id) 
