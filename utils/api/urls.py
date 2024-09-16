from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ContactusViewSet, AdminEmailSendingViewSet

# Create a router and register the ContactusViewSet with it
router = DefaultRouter()
router.register(r'contactus', ContactusViewSet, basename='contactus')
router.register(r'admin-email', AdminEmailSendingViewSet, basename='admin-email')

# Define the urlpatterns by including the router.urls
urlpatterns = [
    path('', include(router.urls)),
]

