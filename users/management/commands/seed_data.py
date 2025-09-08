import random
from datetime import date, timedelta
from django.core.management.base import BaseCommand
from django.db import transaction

from farm.models import Address, Farm, FarmUser
from users.models import User
from animals.models import Breed, Classification, Status, Animal
from reproduction.models import ReproductionCycle


#  python manage.py seed_data

class Command(BaseCommand):
    help = 'Popula o banco de dados com dados de exemplo (20 registros por model).'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.NOTICE('Iniciando a populacão do banco de dados...'))

        try:
            with transaction.atomic():
                self.seed_users_and_farms()
                self.seed_reference_data()
                self.seed_animals(num_animals=20)
                self.seed_reproduction_cycles(num_cycles=20)
                self.stdout.write(self.style.SUCCESS('Banco de dados populado com sucesso! 🎉'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Ocorreu um erro: {e}'))
            self.stdout.write(self.style.WARNING('Nenhuma alteração foi salva devido ao erro.'))

    def seed_users_and_farms(self):
        self.stdout.write('Populando usuários e fazendas...')
        user1, _ = User.objects.get_or_create(username='owner1',
                                              defaults={'name': 'Carlos Mota', 'email': 'carlos@fazenda.com'})

        address1, _ = Address.objects.get_or_create(rua='Rua Principal',
                                                    defaults={'cep': '12345-678', 'bairro': 'Centro',
                                                              'cidade': 'Guarapuava', 'estado': 'Paraná'})

        farm1, _ = Farm.objects.get_or_create(name='Fazenda Boi Forte', defaults={'address': address1})

        FarmUser.objects.get_or_create(farm=farm1, user=user1, defaults={'is_owner': True})

        for i in range(2, 5):
            user, _ = User.objects.get_or_create(username=f'user{i}',
                                                 defaults={'name': f'Usuário {i}', 'email': f'user{i}@fazenda.com'})
            FarmUser.objects.get_or_create(farm=farm1, user=user, defaults={'is_owner': False})

        self.stdout.write(self.style.SUCCESS('Usuários e Fazendas criados.'))

    def seed_reference_data(self):
        self.stdout.write('Populando dados de referência (Raças, Classificações, Status)...')
        breeds = ['Nelore', 'Angus', 'Brahman', 'Hereford', 'Holandês', 'Girolando', 'Guzerá', 'Tabapuã', 'Simental',
                  'Limousin']
        classifications = ['Corte', 'Leite', 'Misto', 'Reprodutor', 'Matriz', 'Novilho', 'Novilha', 'Bezerro',
                           'Bezerra', 'Garrote']
        statuses = ['Saudável', 'Em Lactação', 'Seco', 'Doente', 'Em Reprodução', 'Vendido', 'Falecido',
                    'Em Tratamento', 'Afastado', 'Em Quarentena']

        Breed.objects.bulk_create([Breed(name=name) for name in breeds], ignore_conflicts=True)
        Classification.objects.bulk_create([Classification(name=name) for name in classifications],
                                           ignore_conflicts=True)
        Status.objects.bulk_create([Status(name=name) for name in statuses], ignore_conflicts=True)

        self.stdout.write(self.style.SUCCESS('Dados de referência criados.'))

    def seed_animals(self, num_animals=20):
        self.stdout.write(f'Populando {num_animals} animais...')
        farm = Farm.objects.get(name='Fazenda Boi Forte')
        breeds = list(Breed.objects.all())
        classifications = list(Classification.objects.all())
        statuses = list(Status.objects.all())

        animals = []
        for i in range(num_animals // 2):
            animals.append(Animal(
                identifier=f'VACA-{i:03d}',
                name=f'Fêmea {i}',
                sex='female',
                born_date=date.today() - timedelta(days=random.randint(730, 3650)),
                breed=random.choice(breeds),
                classification=random.choice(classifications),
                status=random.choice(statuses),
                farm=farm
            ))
            animals.append(Animal(
                identifier=f'TOURO-{i:03d}',
                name=f'Macho {i}',
                sex='male',
                born_date=date.today() - timedelta(days=random.randint(730, 3650)),
                breed=random.choice(breeds),
                classification=random.choice(classifications),
                status=random.choice(statuses),
                farm=farm
            ))

        Animal.objects.bulk_create(animals)
        self.stdout.write(self.style.SUCCESS(f'{len(animals)} animais criados.'))

    def seed_reproduction_cycles(self, num_cycles=20):
        self.stdout.write(f'Populando {num_cycles} ciclos reprodutivos...')
        female_animals = list(Animal.objects.filter(sex='female'))
        male_animals = list(Animal.objects.filter(sex='male'))

        if not female_animals or not male_animals:
            self.stdout.write(self.style.WARNING('Não há animais suficientes para criar ciclos reprodutivos. Pulando.'))
            return

        cycles = []
        for i in range(num_cycles):
            female = random.choice(female_animals)
            mating_type = random.choice(['natural', 'artificial'])
            mating_date = date.today() - timedelta(days=random.randint(10, 300))

            cycle = ReproductionCycle(
                female_animal=female,
                heat_start_date=mating_date - timedelta(days=1),
                mating_date=mating_date,
                mating_type=mating_type,
                male_animal=random.choice(male_animals) if mating_type == 'natural' else None,
                status='active',
            )
            cycles.append(cycle)

        ReproductionCycle.objects.bulk_create(cycles)
        self.stdout.write(self.style.SUCCESS(f'{len(cycles)} ciclos reprodutivos criados.'))