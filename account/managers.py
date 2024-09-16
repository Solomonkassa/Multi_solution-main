from django.contrib.auth.models import BaseUserManager

class UserManager(BaseUserManager):
    """
    Custom user manager for creating and managing users.
    """

    def create_user(
        self,
        first_name,
        phone_number,
        password=None,
        email=None,
        username=None,
        last_name=None,
        is_active=True,
        is_staff=False,
        is_superuser=False,
        is_trainee=False,
    ):
        """
        Create a new user.
        """
        if not first_name:
            raise ValueError("First name is required")
        if not phone_number:
            raise ValueError("Phone number is required")

        if email:
            email = self.normalize_email(email)

        user = self.model(
            email=email,
            first_name=first_name,
            phone_number=phone_number,
            is_active=is_active,
            is_staff=is_staff,
            is_superuser=is_superuser,
            last_name=last_name,
            username=username,
            is_trainee=is_trainee,
        )
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(
        self,
        first_name,
        phone_number,
        password,
        username=None,
        email=None,
        last_name=None,
        is_active=True,
        is_superuser=True,
        is_staff=True,
    ):
        """
        Create a new superuser.
        """
        user = self.create_user(
            first_name=first_name,
            phone_number=phone_number,
            password=password,
            email=email,
            username=username,
            last_name=last_name,
            is_active=is_active,
            is_staff=is_staff,
            is_superuser=is_superuser,
        )
        user.is_phone_verified = True
        user.is_email_verified = True
        user.save(using=self._db)
        return user


class TraineeManager(UserManager):
    """
    Custom user manager for Trainees.
    """

    def get_queryset(self):
        """
        Get queryset of Trainees.
        """
        return super().get_queryset().filter(is_trainee=True)


class StaffManager(UserManager):
    """
    Custom user manager for Staff.
    """

    def get_queryset(self):
        """
        Get queryset of Staff.
        """
        return super().get_queryset().filter(is_staff=True)
