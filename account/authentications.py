from django.contrib.auth import backends, get_user_model
from django.db.models import Q

User = get_user_model()

class AuthBackend(backends.BaseBackend):
    """
    Custom authentication backend for handling user authentication.
    """

    def authenticate(
        self, request, username=None, phone_number=None, password=None, clear_otp=True
    ):
        """
        Authenticate user based on username (phone number) and password.
        """
        if not username:
            username = phone_number
        # Query user by username (case insensitive) or normalized phone number
        user = User.objects.filter(
            Q(username__iexact=username)
            | Q(phone_number__exact=User.normalize_phone(username))
        ).first()

        if not user:
            return None

        # Check if the password is correct
        if not user.check_password(password):
            return None
        # Check if the user's phone is verified
        if user.is_phone_verified:
            return user
        return None

    def get_user(self, user_id):
        """
        Retrieve user object by user ID.
        """
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
