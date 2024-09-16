from django.urls import path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework.routers import DefaultRouter
from .views import   TraineeViewsets, UserViewsets, PreferenceViewSet, hook,  ForgotPasswordView,  LoginView,  ResetPasswordView, StaffViewsets, VerifyOTPView

router = DefaultRouter()
router.register(r"trainee", TraineeViewsets, basename="trainee")
router.register(r"users", UserViewsets, basename="users")
router.register(r"staff", StaffViewsets, basename="staff")
router.register(r"preference", PreferenceViewSet, basename="preference")

urlpatterns = [
    # Authentication endpoints for Trainees
    
    path("web-hook", hook, name="web-hook"),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('login/', LoginView.as_view(), name='login'),
    path('forgot-password/', ForgotPasswordView.as_view(), name='forgot-password'),
    path('reset-password/', ResetPasswordView.as_view(), name='reset-password'),
    path('verify-otp/', VerifyOTPView.as_view(), name='verify-otp'),

]

urlpatterns += router.urls


