from django.contrib import admin
from .models import BankAccount, TraineePayment, MonthlyPayment, MonthlyPaymentCycle

@admin.register(BankAccount)
class BankAccountAdmin(admin.ModelAdmin):
    list_display = ('account_number', 'account_name', 'bank_name')
    search_fields = ('account_number', 'account_name', 'bank_name')

@admin.register(TraineePayment)
class TraineePaymentAdmin(admin.ModelAdmin):
    list_display = ('user', 'is_completed', 'is_rejected', 'amount', 'get_bank', 'get_trans_num',  'created_at')
    list_filter = ('is_completed',)
    search_fields = ('user__username', 'user__email')

    def get_bank(self, obj):
        return obj.get_bank()
    get_bank.short_description = 'Bank Name'

    def get_trans_num(self, obj):
        return obj.get_trans_num()
    get_trans_num.short_description = 'Transaction Number'


@admin.register(MonthlyPayment)
class MonthlyPaymentAdmin(admin.ModelAdmin):
    list_display = ('user', 'trans_num', 'account_options', 'is_completed', 'is_rejected', 'created_at')
    list_filter = ('is_completed', 'created_at')
    search_fields = ('user__username', 'trans_num')
    date_hierarchy = 'created_at'
    
@admin.register(MonthlyPaymentCycle)
class MonthlyPaymentCycleAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'opening_date', 'closing_date', 'is_active')
    list_filter = ('is_active',)
    search_fields = ['opening_date', 'closing_date']
    ordering = ('-opening_date',)
    readonly_fields = ('is_active',)