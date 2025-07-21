from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AnimalViewSet

router = DefaultRouter()
# Mude o prefixo do registro de 'animals' para 'animals' (sem o 's' extra)
# para que a URL se torne /api/animals/
router.register(r'animals', AnimalViewSet, basename='animal')

urlpatterns = [
    path('', include(router.urls)),
]