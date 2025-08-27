from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AnimalViewSet

router = DefaultRouter()
router.register(r'animals', AnimalViewSet, basename='animal')

urlpatterns = [
    path('', include(router.urls)),
]