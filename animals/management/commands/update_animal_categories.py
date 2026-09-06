from django.core.management.base import BaseCommand
from animals.models import Animal


class Command(BaseCommand):
    help = 'Atualiza as categorias zootécnicas dos animais com base na idade para fazendas com automação ativa.'

    def handle(self, *args, **options):
        # Busca apenas animais de fazendas que possuem a automação ligada
        animals = Animal.objects.filter(
            farm__auto_update_categories=True
        ).select_related('farm')

        updated_count = 0
        for animal in animals:
            old_category = animal.category
            animal.update_category_by_age()

            if animal.category != old_category:
                animal.save(update_fields=['category'])
                updated_count += 1

        self.stdout.write(
            self.style.SUCCESS(f'Sucesso: {updated_count} categorias de animais foram atualizadas.')
        )
