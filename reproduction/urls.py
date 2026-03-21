from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ReproductionCycleViewSet, SemenDonorViewSet

router = DefaultRouter()
router.register(r'reproductions', ReproductionCycleViewSet, basename='reproductions')
router.register(r'donors', SemenDonorViewSet, basename='semen-donor')

urlpatterns = [
    path('', include(router.urls)),
]