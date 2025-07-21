from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/users/', include('users.urls')),
    # path('api/v1/farm/', include('farm.urls')),
    path('api/', include('animals.urls')),
]
