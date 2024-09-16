# account/validators.py
from django.core.exceptions import ValidationError

def validate_unique_trans_num(value):
    from account.models import User
    from finance.models import MonthlyPayment

    if User.objects.filter(trans_num=value).exists():
        raise ValidationError(f"A user with the transaction number '{value}' already exists.")
    if MonthlyPayment.objects.filter(trans_num=value).exists():
        raise ValidationError(f"A payment with the transaction number '{value}' already exists.")

