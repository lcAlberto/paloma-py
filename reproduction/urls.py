from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ReproductionCycleViewSet

router = DefaultRouter()
router.register(r'reproductions', ReproductionCycleViewSet, basename='reproductions')

urlpatterns = [
    path('', include(router.urls)),
]