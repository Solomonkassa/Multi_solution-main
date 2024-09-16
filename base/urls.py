from django.contrib import admin
from django.urls import path, include, re_path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework.permissions import AllowAny

# Create a schema view for API documentation
schema_view = get_schema_view(
    openapi.Info(
        title="Multi Solution API",
        default_version='1.0.0',
        description="Multi Solution API",
        contact=openapi.Contact(email="multisolution @outlook.com"),
       
    ),
    public=True,
    permission_classes=(AllowAny,), 
)

# Define the urlpatterns for your Django project
urlpatterns = [
    # Admin site
    path('admin/', admin.site.urls),

    path('enrollment/', include('enrollment.api.urls')),
    path('account/', include('account.api.urls')),
    path('finance/', include('finance.api.urls')),
    path('utils/', include('utils.api.urls')),
    # Djoser authentication URLs
    #path('auth/', include('djoser.urls')),
    #path('auth/', include('djoser.urls.jwt')),
    # API documentation endpoints
    re_path(r'^api/docs(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('api/docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]

