from django.contrib import admin
from .models import Breed, Classification, Status, Animal

@admin.register(Animal)
class AnimalAdmin(admin.ModelAdmin):
    list_display = ('name', 'identifier', 'farm')
    list_filter = ('farm',)

admin.site.register(Breed)
admin.site.register(Classification)
admin.site.register(Status)
