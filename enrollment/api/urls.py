from django.urls import include, path
from rest_framework_nested import routers
from . import views

router = routers.DefaultRouter()
router.register('training', views.TrainingViewSet, basename='courses')
router.register('enrollments', views.EnrollmentViewSet, basename='enrollments')

urlpatterns = [
    path('', include(router.urls)),
]
