from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView
from django.urls import path, include

urlpatterns = [
    # Génération du schéma OpenAPI
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),

    # Swagger UI
    path('swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),

    # ReDoc (optionnel)
    path('redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),

    path('eshop/', include('ecommerce.urls')),
]
