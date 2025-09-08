from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import FarmViewSet, AddressViewSet

router = DefaultRouter()
router.register(r'farms', FarmViewSet, basename='farm')
router.register(r'addresses', AddressViewSet, basename='address')

urlpatterns = [
    path('', include(router.urls)),

]