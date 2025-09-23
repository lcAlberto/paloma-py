import random
from datetime import date, timedelta
from django.core.management.base import BaseCommand
from django.db import transaction

from farm.models import Address, Farm, FarmUser
from users.models import User
from animals.models import Breed, Classification, Status, Animal, Comments
from reproduction.models import ReproductionCycle

# PALOMA Sistema de gestão de rebanho
# Este cript popula o banco de dados com registros iniciais para testes, para executar, rode
##### python manage.py seed_data ######

class Command(BaseCommand):
    help = 'Popula o banco de dados com dados de exemplo para testes de paginação.'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.NOTICE('Iniciando a populacão do banco de dados para testes...'))

        try:
            with transaction.atomic():
                self.seed_users_and_farms()
                self.seed_reference_data()
                self.seed_animals(num_animals=35)
                self.seed_reproduction_cycles()
                self.seed_comments()
                self.stdout.write(self.style.SUCCESS('Banco de dados populado com sucesso! 🎉'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Ocorreu um erro: {e}'))
            self.stdout.write(self.style.WARNING('Nenhuma alteração foi salva devido ao erro.'))

    def seed_users_and_farms(self):
        self.stdout.write('Populando usuários e fazendas...')
        farm_names = [
            'Estância da Serra', 'Sítio do Pica-Pau Amarelo', 'Rancho Fundo',
            'Fazenda Ouro Verde', 'Recanto das Águas', 'Fazenda do Vale Encantado'
        ]

        main_user, _ = User.objects.get_or_create(username='owner_principal',
                                                  defaults={'name': 'Dono Fazendeiro', 'email': 'dono@fazenda.com'})

        for name in farm_names:
            address, _ = Address.objects.get_or_create(
                rua=f'Rua {name}',
                defaults={'cep': '12345-678', 'bairro': 'Rural', 'cidade': 'Guarapuava', 'estado': 'Paraná'}
            )
            farm, _ = Farm.objects.get_or_create(name=name, defaults={'address': address})
            FarmUser.objects.get_or_create(farm=farm, user=main_user, defaults={'is_owner': True})

        self.stdout.write(self.style.SUCCESS(f'{len(farm_names)} Fazendas e 1 usuário principal criados.'))

    def seed_reference_data(self):
        self.stdout.write('Populando dados de referência (Raças, Classificações, Status)...')

        breeds = ['Nelore', 'Angus', 'Brahman', 'Holandês', 'Girolando', 'Guzerá', 'Tabapuã']
        Breed.objects.bulk_create([Breed(name=name, isEnabled=True) for name in breeds], ignore_conflicts=True)

        classifications_data = {
            'Rufião': {'isReproducible': True},
            'Garrote': {'isReproducible': True},
            'Novilha': {'isReproducible': True},
            'Touro': {'isReproducible': True},
            'Bezerro': {'isReproducible': False},
            'Bezerra': {'isReproducible': False},
            'Vaca': {'isReproducible': True},
            'Capão': {'isReproducible': False, 'isEnabled': False},
        }
        for name, values in classifications_data.items():
            Classification.objects.get_or_create(name=name, defaults=values)

        statuses_data = {
            'Vaca Seca': {'isReproducible': False},
            'Vaca Leiteira': {'isReproducible': True},
            'Sob Tratamento Clínico': {'isReproducible': False},
            'Amamentação': {'isReproducible': True},
            'Vendido': {'isReproducible': False, 'isEnabled': False},
            'Falecido': {'isReproducible': False, 'isEnabled': False},
        }
        for name, values in statuses_data.items():
            Status.objects.get_or_create(name=name, defaults=values)

        # Adicionei os status de Crescimento e Reprodução
        Status.objects.get_or_create(name='Em Crescimento', defaults={'isReproducible': True})
        Status.objects.get_or_create(name='Em Reprodução', defaults={'isReproducible': True})

        self.stdout.write(self.style.SUCCESS('Dados de referência criados.'))

    def seed_animals(self, num_animals=35):
        self.stdout.write(f'Populando {num_animals} animais...')
        farms = list(Farm.objects.all())
        breeds = list(Breed.objects.all())

        animal_names_male = ['Ferdinando', 'Gerso', 'Sansão', 'Touro Bandido', 'Pé de Pano', 'Zeus', 'Girso', 'Thor',
                             'Apollo']
        animal_names_female = ['Mimosa', 'Sinfra', 'Rebeca', 'Filó', 'Pitty', 'Sequinha', 'Janaína', 'Linda',
                               'Cleópatra', 'Rainha', 'Dorotéia', 'Paloma', 'Daniela', 'Fernanda']

        # Buscando todas as classificações e status após a criação
        classifications = {c.name: c for c in Classification.objects.all()}
        statuses = {s.name: s for s in Status.objects.all()}

        animals = []
        for i in range(num_animals):
            sex = random.choice(['male', 'female'])
            is_adult = random.random() > 0.3
            is_dissociated = random.random() < 0.1

            if sex == 'male':
                name = random.choice(animal_names_male)
                if is_adult and not is_dissociated:
                    age_days = random.randint(3 * 365, 10 * 365)
                    classification = random.choice([classifications['Touro'], classifications['Rufião']])
                    status = statuses['Em Reprodução']
                elif not is_adult and not is_dissociated:
                    age_days = random.randint(100, 3 * 365)
                    classification = classifications['Bezerro'] if age_days < 365 else classifications['Garrote']
                    status = statuses['Em Crescimento']
                else:  # Desassociado
                    age_days = random.randint(100, 10 * 365)
                    classification = random.choice([c for c in Classification.objects.all() if c.isEnabled])
                    status = statuses['Vendido'] if random.random() > 0.5 else statuses['Falecido']
                identifier_prefix = 'M-'
            else:  # 'female'
                name = random.choice(animal_names_female)
                if is_adult and not is_dissociated:
                    age_days = random.randint(2 * 365, 12 * 365)
                    classification = classifications['Vaca']
                    status = random.choice([statuses['Vaca Leiteira'], statuses['Vaca Seca'], statuses['Amamentação']])
                elif not is_adult and not is_dissociated:
                    age_days = random.randint(100, 2 * 365)
                    classification = classifications['Bezerra'] if age_days < 365 else classifications['Novilha']
                    status = statuses['Em Crescimento']
                else:  # Desassociado
                    age_days = random.randint(100, 12 * 365)
                    classification = random.choice([c for c in Classification.objects.all() if c.isEnabled])
                    status = statuses['Vendido'] if random.random() > 0.5 else statuses['Falecido']
                identifier_prefix = 'F-'

            identifier = f'{identifier_prefix}{i:03d}'
            while Animal.objects.filter(identifier=identifier).exists():
                i += 1
                identifier = f'{identifier_prefix}{i:03d}'

            is_alive = True
            dissociated_reason = None
            if is_dissociated:
                is_alive = False if status.name == 'Falecido' else True
                dissociated_reason = 'sold' if status.name == 'Vendido' else 'dead'

            animals.append(Animal(
                identifier=identifier,
                name=f'{name} {i}',
                sex=sex,
                born_date=date.today() - timedelta(days=age_days),
                breed=random.choice(breeds),
                classification=classification,
                status=status,
                farm=random.choice(farms),
                is_active=not is_dissociated,
                is_alive=is_alive,
                dissociated_reasons=dissociated_reason,
            ))

        Animal.objects.bulk_create(animals)
        self.stdout.write(self.style.SUCCESS(f'{len(animals)} animais criados.'))

    def seed_reproduction_cycles(self):
        self.stdout.write('Populando ciclos reprodutivos para fêmeas adultas...')
        female_animals = list(Animal.objects.filter(
            classification__name='Vaca',
            sex='female',
            is_active=True,
            status__isReproducible=True
        ))
        male_animals = list(Animal.objects.filter(sex='male', is_active=True, classification__isReproducible=True))

        if not female_animals or not male_animals:
            self.stdout.write(self.style.WARNING('Não há animais adultos suficientes para criar ciclos. Pulando.'))
            return

        cycles = []
        for female in female_animals:
            num_cycles = random.randint(1, 2)
            for _ in range(num_cycles):
                mating_type = random.choice(['natural', 'artificial'])
                mating_date = date.today() - timedelta(days=random.randint(200, 1000))

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

    def seed_comments(self):
        self.stdout.write('Populando comentários para alguns animais...')
        animals_with_comments = random.sample(list(Animal.objects.all()), min(10, Animal.objects.count()))
        user = User.objects.first()
        comments_list = [
            'Animal com bom desenvolvimento.',
            'Apresentou febre alta, administrado antibiótico.',
            'Vaca com boa produção de leite, acima da média.',
            'Precisando de reforço na alimentação.',
            'Bezerro saudável e muito ativo.',
            'Touro com comportamento um pouco agressivo.',
            'Observar sinais de cio nos próximos dias.',
            'Peso estável, ótimo desenvolvimento.',
        ]

        if not user:
            self.stdout.write(self.style.WARNING('Nenhum usuário encontrado para criar comentários. Pulando.'))
            return

        comments = []
        for animal in animals_with_comments:
            num_comments = random.randint(1, 3)
            for _ in range(num_comments):
                comment_text = random.choice(comments_list)
                comments.append(Comments(animal=animal, user=user, comment=comment_text))

        Comments.objects.bulk_create(comments)
        self.stdout.write(self.style.SUCCESS(f'{len(comments)} comentários criados.'))