from rest_framework import serializers
from finance.models import BankAccount, TraineePayment, MonthlyPayment, MonthlyPaymentCycle 


class BankAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = BankAccount
        fields = '__all__'

class MonthlyPaymentCycleSerializer(serializers.ModelSerializer):
    class Meta:
        model = MonthlyPaymentCycle
        fields = '__all__'
        
class PaymentSerializer(serializers.ModelSerializer):
    trans_num = serializers.SerializerMethodField()
    first_name = serializers.CharField(source='user.first_name', read_only=True)
    middle_name = serializers.CharField(source='user.middle_name', read_only=True) 
    last_name = serializers.CharField(source='user.last_name', read_only=True)
    training = serializers.CharField(source='user.training', read_only=True)
    phone_number = serializers.CharField(source='user.phone_number', read_only=True)
    bank_name = serializers.CharField(source='user.account_options.bank_name', read_only=True)
    trans_num = serializers.CharField(source='user.trans_num', read_only=True)

    class Meta:
        abstract = True
        fields = ['trans_num', 'user', 'first_name','bank_name','amount', 'is_completed', 'is_rejected', 'created_at']

    def get_bank(self, obj):
        """
        Get bank details associated with the user, if available.
        """
        return obj.get_bank()

    def get_trans_num(self, obj):
        """
        Get transaction number associated with the user, if available.
        """
        return obj.get_trans_num()

class TraineePaymentSerializer(PaymentSerializer):
    class Meta(PaymentSerializer.Meta):
        model = TraineePayment
        fields = '__all__'



class MonthlyPaymentSerializer(serializers.ModelSerializer):

    first_name = serializers.CharField(source='user.first_name', read_only=True)
    middle_name = serializers.CharField(source='user.middle_name', read_only=True) 
    last_name = serializers.CharField(source='user.last_name', read_only=True)
    bank_name = serializers.CharField(source='account_options.bank_name', read_only=True)
    schedule = serializers.CharField(source='cycle', read_only=True)
    training = serializers.CharField(source='user.training', read_only=True)
    phone_number = serializers.CharField(source='user.phone_number', read_only=True)
    class Meta:
        model = MonthlyPayment
        fields = ['trans_num', 'user', 'first_name','middle_name','last_name', 'phone_number','cycle','bank_name','schedule','training', 'amount', 'is_completed', 'is_rejected', 'created_at']
