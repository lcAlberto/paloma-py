# farm/views.py
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from .models import Farm, FarmUser, Address
from .serializers import FarmSerializer, AddressSerializer
from .permissions import IsOwnerPermission

class FarmViewSet(viewsets.ModelViewSet):
    serializer_class = FarmSerializer
    permission_classes = [IsAuthenticated, IsOwnerPermission]

    def get_queryset(self):
        user = self.request.user
        return user.farms.all()

    def perform_create(self, serializer):
        farm = serializer.save()
        # usuário que criou a fazenda éo proprietário
        FarmUser.objects.create(farm=farm, user=self.request.user, is_owner=True)


class AddressViewSet(viewsets.ModelViewSet):
    queryset = Address.objects.all()
    serializer_class = AddressSerializer
    permission_classes = [IsAuthenticated]