from django.contrib import admin
from .models import Breed, Classification, Status, Animal

@admin.register(Animal)
class AnimalAdmin(admin.ModelAdmin):
    list_display = ('name', 'identifier', 'farm')
    list_filter = ('farm',)
    search_fields = ['name', 'identifier']


@admin.register(Breed)
class BreedAdmin(admin.ModelAdmin):
    list_display = ('name', 'value', 'isEnabled', 'average_gestation_days')
    list_filter = ('name', 'value', 'isEnabled', 'average_gestation_days',)
    search_fields = ['name', 'value']

admin.site.register(Classification)
admin.site.register(Status)
