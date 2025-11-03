from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    AnimalViewSet,
    BreedViewSet,
    ClassificationViewSet,
    StatusViewSet,
    ParentsListAPIView,
)

router = DefaultRouter()
router.register(r'animals', AnimalViewSet, basename='animal')
# router.register(r'parents', ParentsListAPIView, basename='parent-list')
router.register(r'breeds', BreedViewSet, basename='breeds')
router.register(r'classifications', ClassificationViewSet, basename='classifications')
router.register(r'statuses', StatusViewSet, basename='statuses')

urlpatterns = [
    path('', include(router.urls)),
    path('parents/', ParentsListAPIView.as_view(), name='parent-list')
]