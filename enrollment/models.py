from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

class Training(models.Model):
    """
    Model representing a training.
    """
    

    training = models.CharField(max_length=255, verbose_name=_("Training"))
    price = models.PositiveSmallIntegerField(default=12000)
    created_at = models.DateTimeField(
        default=timezone.now, verbose_name=_("Created At")
    )
    is_active = models.BooleanField(default=True)

    @classmethod
    def get_course_by_department(cls, training_training):
        """
        Get  based on its training.
        """
        return cls.objects.get(training=training_training)
   
    def __str__(self):
        return f"{self.training}"


        
class Enrollment(models.Model):
    """
    Model representing a user's enrollment in a training.
    """
    user = models.OneToOneField(
        settings.TRAINEE_MODEL,  
        related_name="enrollment",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text="The user enrolled in the training.",
    )
    training = models.ForeignKey(
        Training,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="enrollments",
        help_text="The training in which the user is enrolled.",
    )
    enrollment_date = models.DateTimeField(
        auto_now_add=True,
        help_text="The date and time of enrollment.",
    )
    is_complete = models.BooleanField(default=False)
    def __str__(self):
        """
        String representation of the enrollment.
        """
        return f"Enrollment: {self.user}, {self.training}"

    class Meta:
        verbose_name = "Enrollment"
        verbose_name_plural = "Enrollments"
