# notifications/tasks.py ou management/commands/check_daily_alerts.py
from datetime import date, timedelta
from reproduction.models import ReproductionCycle
from notifications.services import NotificationService

def check_upcoming_calvings():
    """Verifica partos previstos de acordo com o prazo configurado em cada fazenda."""
    cycles = ReproductionCycle.objects.filter(
        status='active',
        predicted_calving_date__isnull=False
    ).select_related('female_animal', 'female_animal__farm')

    today = date.today()

    for cycle in cycles:
        farm = cycle.female_animal.farm
        days_before = farm.notify_calving_days_before
        target_date = cycle.predicted_calving_date.date()

        # Se a data de hoje bater com a janela do alerta
        if (target_date - today).days == days_before:
            NotificationService.send_farm_alert(
                farm=farm,
                title=f"Aviso de Parto Próximo: {cycle.female_animal.name}",
                message=f"A fêmea {cycle.female_animal.name} ({cycle.female_animal.identifier}) está prevista para parir em {target_date.strftime('%d/%m/%Y')} (em {days_before} dias).",
                category='reproduction',
                priority='high',
                target_object_type='animal',
                target_object_id=cycle.female_animal.id
            )