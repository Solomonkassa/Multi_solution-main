from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BankAccountViewSet, TraineePaymentViewSet, MonthlyPaymentViewSet,MonthlyPaymentCycleViewSet

# Create a router and register the viewsets with it
router = DefaultRouter()
router.register(r'bank-accounts', BankAccountViewSet, basename='bank-account')
router.register(r'trainee-payments', TraineePaymentViewSet, basename='trainee-payment')
router.register(r'monthly-payments', MonthlyPaymentViewSet, basename='monthly-payment')
router.register(r'monthly-payment-cycle',MonthlyPaymentCycleViewSet, basename='monthly-payment-cycle')

urlpatterns = [
    path('', include(router.urls)),
]

