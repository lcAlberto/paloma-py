from django.contrib import admin
from .models import ReproductionCycle, SemenDonor


@admin.register(SemenDonor)
class SemenDonorAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'registration_number',
        'breed',
        'origin_farm_name',
        'collection_date'
    )
    search_fields = ('name', 'registration_number', 'breed', 'origin_farm_name', 'collection_date')
    list_filter = ('name', 'registration_number', 'breed', 'origin_farm_name', 'collection_date')
    # autocomplete_fields = ['registration_number', 'breed', 'origin_farm_name', 'collection_date']

@admin.register(ReproductionCycle)
class ReproductionCycleAdmin(admin.ModelAdmin):
    list_display = (
        'female_animal',
        'mating_date',
        'mating_type',
        'get_father_display',
        'predicted_calving_date',
        'actual_calving_date',
        'status',
    )
    autocomplete_fields = ['female_animal', 'male_animal', 'calf_born',]
    list_filter = ('status', 'mating_type', 'female_animal__farm')
    search_fields = ('female_animal__name', 'male_animal__name', 'semen_donor__name', 'identifier')
    raw_id_fields = ('female_animal', 'male_animal', 'semen_donor', 'calf_born')
    fieldsets = (
        (None, {
            'fields': (
                'female_animal',
                'heat_start_date',
                'mating_date',
                'mating_type',
                'male_animal',
                'semen_donor',
                'status'
            )
        }),
        ('Parto e Bezerro', {
            'fields': ('predicted_calving_date', 'actual_calving_date', 'calf_born'),
            'classes': ('collapse',),
        }),
    )

    def get_father_display(self, obj):
        if obj.mating_type == 'natural' and obj.male_animal:
            return f"Touro: {obj.male_animal.name}"
        elif obj.mating_type == 'artificial' and obj.semen_donor:
            return f"Doador: {obj.semen_donor.name}"
        return "N/A"
    get_father_display.short_description = 'Pai/Doador'
