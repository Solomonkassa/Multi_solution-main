from django.db import models, IntegrityError
from django.core.validators import MinValueValidator
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from enrollment.models import Enrollment
from account.validators import validate_unique_trans_num

class BankAccount(models.Model):
    """
    Model representing a bank account.
    """

    account_number = models.CharField(max_length=255, verbose_name=_("Account Number"))
    account_name = models.CharField(max_length=255, verbose_name=_("Account Name"))
    bank_name = models.CharField(max_length=255, verbose_name=_("Bank Name"))

    class Meta:
        verbose_name = _("Bank Account")
        verbose_name_plural = _("Bank Accounts")

    def __str__(self):
        return f"{self.bank_name} ({self.account_number})"


class PaymentBase(models.Model):
    """
    Abstract base model representing a payment.
    """

    user = models.ForeignKey(
        settings.TRAINEE_MODEL,
        on_delete=models.CASCADE,
        related_name="%(class)s_payments",
        related_query_name="%(class)s_payment",
        verbose_name=_("Trainee"),
    )

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name=_("Amount"),
    )
    is_completed = models.BooleanField(default=False, verbose_name=_("Is Completed"))
    is_rejected = models.BooleanField(default=False, verbose_name=_("Is Rejected"))
    created_at = models.DateTimeField(default=timezone.now, verbose_name=_("Created At"))

    class Meta:
        abstract = True

    def get_bank(self):
        """
        Get bank details associated with the user, if available.
        """
        return getattr(self.user, 'account_options', None)

    def get_trans_num(self):
        """
        Get transaction number associated with the user, if available.
        """
        return getattr(self.user, 'trans_num', None)

    def save(self, *args, **kwargs):
        """
        Override save method to handle additional logic.
        """
        super().save(*args, **kwargs)
        if self.is_completed:
            training = getattr(self.user, 'training', None)
            if training:
                try:
                    enrollment, created = Enrollment.objects.get_or_create(
                        user=self.user, training=training
                    )
                    if created or not enrollment.is_complete:
                        enrollment.is_complete = True
                        enrollment.save()
                except IntegrityError:
                    pass
        else:
            # Delete enrollment if it exists
            training = getattr(self.user, 'training', None)
            try:
                enrollment = Enrollment.objects.get(user=self.user, training=training)
                enrollment.delete()
            except Enrollment.DoesNotExist:
                pass
        

class TraineePayment(PaymentBase):
    """
    Model representing a trainee payment.
    """

    class Meta:
        verbose_name = _("Trainee Payment")
        verbose_name_plural = _("Trainee Payments")

    def __str__(self):
        return f"Payment for {self.user}: {self.amount} ETB"

    def save(self, *args, **kwargs):
        """
        Override save method to ensure user is a trainee.
        """
        if not getattr(self.user, 'is_trainee', False):
            raise ValidationError(_("User must be a trainee to create a trainee payment."))
        super().save(*args, **kwargs)



class MonthlyPaymentCycle(models.Model):
    """
    Model representing a cycle for monthly payments.
    """

    opening_date = models.DateTimeField(verbose_name=_("Opening Date"))
    closing_date = models.DateTimeField(verbose_name=_("Closing Date"))
    is_active = models.BooleanField(default=True, verbose_name=_("Is Active"))

    class Meta:
        verbose_name = _("Monthly Payment Cycle")
        verbose_name_plural = _("Monthly Payment Cycles")

    def __str__(self):
        opening_str = self.opening_date.strftime("%B %d, %Y")
        closing_str = self.closing_date.strftime("%B %d, %Y")
        return f"{opening_str} to {closing_str}"

    def clean(self):
        """
        Ensure the closing date is after the opening date.
        """
        if self.closing_date <= self.opening_date:
            raise ValidationError(_("Closing date must be after the opening date."))

    def save(self, *args, **kwargs):
        """
        Ensure only one active cycle exists.
        """
        if self.is_active:
            # Deactivate other active cycles
            MonthlyPaymentCycle.objects.exclude(pk=self.pk).update(is_active=False)
        super().save(*args, **kwargs)
        

class MonthlyPayment(models.Model):
    """
    Model representing a monthly payment.
    """

    user = models.ForeignKey(
        settings.TRAINEE_MODEL,
        on_delete=models.CASCADE,
        related_name="monthly_payments",
        related_query_name="monthly_payment",
        verbose_name=_("Trainee"),
    )
    
    trans_num = models.CharField(
        max_length=20,
        unique=True,
        null=True,
        blank=False,
        verbose_name=_("Transaction Number"),
        help_text=_("Required. Bank's unique transaction number."),
        error_messages={"unique": _("A payment with that transaction number already exists.")},
        validators=[validate_unique_trans_num],
    )

    account_options = models.ForeignKey(
        BankAccount,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="monthly_payments",
        verbose_name=_("Bank Account"),
    )
    
    cycle = models.ForeignKey(
        MonthlyPaymentCycle,
        on_delete=models.CASCADE,
        related_name="payments",
        verbose_name=_("Payment Cycle"),
        null=True, 
        blank=True,
    )
    
    
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        default=0.00,
        verbose_name=_("Amount"),
    )
    
    is_completed = models.BooleanField(
        default=False,
        verbose_name=_("Is Completed"),
        help_text=_("Specifies if the payment is completed."),
    )
    
    is_rejected = models.BooleanField(default=False, verbose_name=_("Is Rejected"))
    
    created_at = models.DateTimeField(default=timezone.now, verbose_name=_("Created At"))

    class Meta:
        verbose_name = _("Monthly Payment")
        verbose_name_plural = _("Monthly Payments")

    def __str__(self):
        return f"Monthly Payment for {self.user}: {self.amount} ETB"
