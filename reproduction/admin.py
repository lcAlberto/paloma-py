from django.contrib import admin
from .models import ReproductionCycle, SemenDonor
from .utils import get_lunar_phase
from datetime import timedelta

@admin.register(SemenDonor)
class SemenDonorAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'registration_number',
        'breed',
        'origin_farm_name',
        'collection_date'
    )
    search_fields = ('name', 'registration_number', 'breed__name', 'origin_farm_name')
    list_filter = ('breed', 'origin_farm_name', 'collection_date')


@admin.register(ReproductionCycle)
class ReproductionCycleAdmin(admin.ModelAdmin):
    list_display = (
        'female_animal',
        'mating_date',
        'mating_type',
        'get_father_display',
        'predicted_calving_date',
        'get_lunar_phase_display',
        'actual_calving_date',
        'status',
    )
    list_filter = ('status', 'mating_type', 'female_animal__farm', 'female_animal__breed')
    search_fields = ('female_animal__name', 'male_animal__name', 'semen_donor__name')

    # IMPORTANTE: raw_id_fields e autocomplete_fields não devem ser usados no mesmo campo.
    # Mantivemos raw_id_fields para boa performance com muitos registros.
    raw_id_fields = ('female_animal', 'male_animal', 'semen_donor', 'calf_born')

    # 'predicted_calving_date' precisa ser readonly já que o modelo calcula no save()
    readonly_fields = ('predicted_calving_date', 'get_prediction_info')

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
        ('Parto e Estimativa Refinada', {
            'fields': (
                'predicted_calving_date',
                'get_prediction_info',
                'actual_calving_date',
                'calf_born'
            ),
        }),
    )

    def get_father_display(self, obj):
        if obj.mating_type == 'natural' and obj.male_animal:
            return f"Touro: {obj.male_animal.name}"
        elif obj.mating_type == 'artificial' and obj.semen_donor:
            return f"Doador: {obj.semen_donor.name}"
        return "N/A"

    get_father_display.short_description = 'Pai/Doador'

    def get_lunar_phase_display(self, obj):
        """Exibe a fase da lua no dia do parto previsto na listagem."""
        if obj.predicted_calving_date:
            return get_lunar_phase(obj.predicted_calving_date)
        return "-"

    get_lunar_phase_display.short_description = 'Lua Prevista'

    def get_prediction_info(self, obj):
        """Exibe detalhes do intervalo de confiança dentro da tela do formulário."""
        if not obj.predicted_calving_date:
            return "Salve a data de cobertura para calcular."

        calving_date = obj.predicted_calving_date.date() if hasattr(obj.predicted_calving_date,
                                                                    'date') else obj.predicted_calving_date
        start = (calving_date - timedelta(days=5)).strftime("%d/%m/%Y")
        end = (calving_date + timedelta(days=5)).strftime("%d/%m/%Y")
        lunar = get_lunar_phase(calving_date)

        return f"Janela Provável: {start} até {end} (Lua {lunar})"

    get_prediction_info.short_description = 'Intervalo Zootécnico (±5 dias)'