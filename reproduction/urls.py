from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ReproductionCycleViewSet

router = DefaultRouter()
router.register(r'reproduction-cycles', ReproductionCycleViewSet, basename='reproduction-cycle')

urlpatterns = [
    path('', include(router.urls)),
]