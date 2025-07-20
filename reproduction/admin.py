from django.contrib import admin
from .models import ReproductionCycle

@admin.register(ReproductionCycle)
class ReproductionCycleAdmin(admin.ModelAdmin):
    list_display = (
        'female_animal',
        'mating_date',
        'mating_type',
        'predicted_calving_date',
        'actual_calving_date',
        'status',
    )
    list_filter = ('status', 'mating_type', 'female_animal__farm')
    search_fields = ('female_animal__name', 'male_animal__name', 'identifier')
    raw_id_fields = ('female_animal', 'male_animal', 'calf_born')
    fieldsets = (
        (None, {
            'fields': ('female_animal', 'heat_start_date', 'mating_date', 'mating_type', 'male_animal', 'status')
        }),
        ('Parto e Bezerro', {
            'fields': ('predicted_calving_date', 'actual_calving_date', 'calf_born'),
            'classes': ('collapse',),
        }),
    )