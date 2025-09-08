from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/users/', include('users.urls')),
    path('api/', include('farm.urls')),
    path('api/', include('animals.urls')),
    path('api/', include('reproduction.urls')),
]
