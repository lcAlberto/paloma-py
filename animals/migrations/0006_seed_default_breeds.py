from django.db import migrations


def seed_breeds(apps, schema_editor):
    Breed = apps.get_model('animals', 'Breed')

    # Mapeamento padrão zootécnico para as raças mais comuns no Brasil
    default_breeds = [
        {"name": "Nelore", "value": "nelore", "average_gestation_days": 291},
        {"name": "Gir Leiteiro", "value": "gir_leiteiro", "average_gestation_days": 288},
        {"name": "Guzerá", "value": "guzera", "average_gestation_days": 292},
        {"name": "Holandês", "value": "holandes", "average_gestation_days": 279},
        {"name": "Jersey", "value": "jersey", "average_gestation_days": 279},
        {"name": "Girolando (5/8)", "value": "girolando_5_8", "average_gestation_days": 283},
        {"name": "Girolando (3/8)", "value": "girolando_3_8", "average_gestation_days": 285},
        {"name": "Angus", "value": "angus", "average_gestation_days": 281},
        {"name": "Simental", "value": "simental", "average_gestation_days": 285},
        {"name": "Outra / Indefinida", "value": "other", "average_gestation_days": 283},
    ]

    for breed_data in default_breeds:
        Breed.objects.update_or_create(
            name=breed_data["name"],
            defaults={
                "value": breed_data["value"],
                "average_gestation_days": breed_data["average_gestation_days"],
                "isEnabled": True
            }
        )


def reverse_seed(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    dependencies = [
        ('animals', '0005_breed_average_gestation_days'), 
    ]

    operations = [
        migrations.RunPython(seed_breeds, reverse_seed),
    ]