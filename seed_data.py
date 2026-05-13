import os
import django
from datetime import date, timedelta
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from shop.models import Game, GameKey

# Удалим старые игры
Game.objects.all().delete()

# Тестовые данные
games_data = [
    {
        'title': 'The Witcher 3: Wild Hunt',
        'description': 'Ролевая игра в открытом мире с потрясающей историей и богатым миром.',
        'developer': 'CD Projekt Red',
        'publisher': 'CD Projekt',
        'release_date': date(2015, 5, 19),
        'platform': 'steam',
        'genre': 'rpg',
        'region': 'Global',
        'system_requirements': 'OS: Windows 7, Windows 8, Windows 10\nCPU: Intel i5-2500K or AMD equivalent\nRAM: 8 GB\nGPU: NVIDIA GTX 960 or AMD equivalent\nDisk: 150 GB',
        'price': Decimal('2999.00'),
        'discount_percent': 20,
    },
    {
        'title': 'Cyberpunk 2077',
        'description': 'Научно-фантастический экшен в мегаполисе будущего.',
        'developer': 'CD Projekt Red',
        'publisher': 'CD Projekt',
        'release_date': date(2020, 12, 10),
        'platform': 'steam',
        'genre': 'action',
        'region': 'Global',
        'price': Decimal('3499.00'),
        'discount_percent': 30,
    },
    {
        'title': 'Elden Ring',
        'description': 'Action RPG от From Software и George R. R. Martin.',
        'developer': 'FromSoftware',
        'publisher': 'Bandai Namco',
        'release_date': date(2022, 2, 25),
        'platform': 'steam',
        'genre': 'action',
        'region': 'Global',
        'price': Decimal('3999.00'),
        'discount_percent': 0,
    },
    {
        'title': 'Baldur\'s Gate 3',
        'description': 'Легендарная CRPG, адаптация настольной игры D&D.',
        'developer': 'Larian Studios',
        'publisher': 'Larian Studios',
        'release_date': date(2023, 8, 3),
        'platform': 'steam',
        'genre': 'rpg',
        'region': 'Global',
        'price': Decimal('3999.00'),
        'discount_percent': 15,
    },
    {
        'title': 'Hades',
        'description': 'Инди-экшен рогалик от Supergiant Games.',
        'developer': 'Supergiant Games',
        'publisher': 'Supergiant Games',
        'release_date': date(2020, 9, 17),
        'platform': 'epic',
        'genre': 'indie',
        'region': 'Global',
        'price': Decimal('1999.00'),
        'discount_percent': 25,
    },
    {
        'title': 'Starfield',
        'description': 'Научно-фантастическая RPG от Bethesda.',
        'developer': 'Bethesda Game Studios',
        'publisher': 'Bethesda Softworks',
        'release_date': date(2023, 9, 6),
        'platform': 'steam',
        'genre': 'rpg',
        'region': 'Global',
        'price': Decimal('3999.00'),
        'discount_percent': 0,
    },
    {
        'title': 'Hogwarts Legacy',
        'description': 'Приключение в мире Гарри Поттера.',
        'developer': 'Avalanche Software',
        'publisher': 'Warner Bros. Games',
        'release_date': date(2023, 2, 10),
        'platform': 'steam',
        'genre': 'action',
        'region': 'Global',
        'price': Decimal('3499.00'),
        'discount_percent': 35,
    },
    {
        'title': 'Portal 2',
        'description': 'Легендарная головоломка с порталами.',
        'developer': 'Valve',
        'publisher': 'Valve',
        'release_date': date(2011, 4, 18),
        'platform': 'steam',
        'genre': 'puzzle',
        'region': 'Global',
        'price': Decimal('799.00'),
        'discount_percent': 50,
    },
    {
        'title': 'Team Fortress 2',
        'description': 'Бесплатный мультиплеерный шутер от Valve.',
        'developer': 'Valve',
        'publisher': 'Valve',
        'release_date': date(2007, 10, 10),
        'platform': 'steam',
        'genre': 'shooter',
        'region': 'Global',
        'price': Decimal('0.00'),
        'discount_percent': 0,
    },
    {
        'title': 'Minecraft',
        'description': 'Игра с открытым миром с блочной графикой.',
        'developer': 'Mojang Studios',
        'publisher': 'Microsoft',
        'release_date': date(2011, 11, 18),
        'platform': 'steam',
        'genre': 'simulation',
        'region': 'Global',
        'price': Decimal('2699.00'),
        'discount_percent': 10,
    },
]

# Создаём игры
for game_data in games_data:
    game = Game.objects.create(**game_data)
    print(f'✓ Создана игра: {game.title}')
    
    # Добавляем тестовые ключи
    for i in range(10):
        key_string = f'{game.id:04d}-{i:04d}-XXXX-XXXX-{game.title[:4].upper()}'
        GameKey.objects.create(
            game=game,
            key=key_string
        )

print('\n✓ Тестовые данные успешно добавлены!')

import os
import django
from datetime import date, timedelta
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from shop.models import Game, GameKey

# Удалим старые игры
Game.objects.all().delete()

# Тестовые данные
games_data = [
    {
        'title': 'The Witcher 3: Wild Hunt',
        'description': 'Ролевая игра в открытом мире с потрясающей историей и богатым миром.',
        'developer': 'CD Projekt Red',
        'publisher': 'CD Projekt',
        'release_date': date(2015, 5, 19),
        'platform': 'steam',
        'genre': 'rpg',
        'region': 'Global',
        'system_requirements': 'OS: Windows 7, Windows 8, Windows 10\nCPU: Intel i5-2500K or AMD equivalent\nRAM: 8 GB\nGPU: NVIDIA GTX 960 or AMD equivalent\nDisk: 150 GB',
        'price': Decimal('2999.00'),
        'discount_percent': 20,
    },
    {
        'title': 'Cyberpunk 2077',
        'description': 'Научно-фантастический экшен в мегаполисе будущего.',
        'developer': 'CD Projekt Red',
        'publisher': 'CD Projekt',
        'release_date': date(2020, 12, 10),
        'platform': 'steam',
        'genre': 'action',
        'region': 'Global',
        'price': Decimal('3499.00'),
        'discount_percent': 30,
    },
    {
        'title': 'Elden Ring',
        'description': 'Action RPG от From Software и George R. R. Martin.',
        'developer': 'FromSoftware',
        'publisher': 'Bandai Namco',
        'release_date': date(2022, 2, 25),
        'platform': 'steam',
        'genre': 'action',
        'region': 'Global',
        'price': Decimal('3999.00'),
        'discount_percent': 0,
    },
    {
        'title': 'Baldur\'s Gate 3',
        'description': 'Легендарная CRPG, адаптация настольной игры D&D.',
        'developer': 'Larian Studios',
        'publisher': 'Larian Studios',
        'release_date': date(2023, 8, 3),
        'platform': 'steam',
        'genre': 'rpg',
        'region': 'Global',
        'price': Decimal('3999.00'),
        'discount_percent': 15,
    },
    {
        'title': 'Hades',
        'description': 'Инди-экшен рогалик от Supergiant Games.',
        'developer': 'Supergiant Games',
        'publisher': 'Supergiant Games',
        'release_date': date(2020, 9, 17),
        'platform': 'epic',
        'genre': 'indie',
        'region': 'Global',
        'price': Decimal('1999.00'),
        'discount_percent': 25,
    },
    {
        'title': 'Starfield',
        'description': 'Научно-фантастическая RPG от Bethesda.',
        'developer': 'Bethesda Game Studios',
        'publisher': 'Bethesda Softworks',
        'release_date': date(2023, 9, 6),
        'platform': 'steam',
        'genre': 'rpg',
        'region': 'Global',
        'price': Decimal('3999.00'),
        'discount_percent': 0,
    },
    {
        'title': 'Hogwarts Legacy',
        'description': 'Приключение в мире Гарри Поттера.',
        'developer': 'Avalanche Software',
        'publisher': 'Warner Bros. Games',
        'release_date': date(2023, 2, 10),
        'platform': 'steam',
        'genre': 'action',
        'region': 'Global',
        'price': Decimal('3499.00'),
        'discount_percent': 35,
    },
    {
        'title': 'Portal 2',
        'description': 'Легендарная головоломка с порталами.',
        'developer': 'Valve',
        'publisher': 'Valve',
        'release_date': date(2011, 4, 18),
        'platform': 'steam',
        'genre': 'puzzle',
        'region': 'Global',
        'price': Decimal('799.00'),
        'discount_percent': 50,
    },
    {
        'title': 'Team Fortress 2',
        'description': 'Бесплатный мультиплеерный шутер от Valve.',
        'developer': 'Valve',
        'publisher': 'Valve',
        'release_date': date(2007, 10, 10),
        'platform': 'steam',
        'genre': 'shooter',
        'region': 'Global',
        'price': Decimal('0.00'),
        'discount_percent': 0,
    },
    {
        'title': 'Minecraft',
        'description': 'Игра с открытым миром с блочной графикой.',
        'developer': 'Mojang Studios',
        'publisher': 'Microsoft',
        'release_date': date(2011, 11, 18),
        'platform': 'steam',
        'genre': 'simulation',
        'region': 'Global',
        'price': Decimal('2699.00'),
        'discount_percent': 10,
    },
]

# Создаём игры
for game_data in games_data:
    game = Game.objects.create(**game_data)
    print(f'✓ Создана игра: {game.title}')
    
    # Добавляем тестовые ключи
    for i in range(10):
        key_string = f'{game.id:04d}-{i:04d}-XXXX-XXXX-{game.title[:4].upper()}'
        GameKey.objects.create(
            game=game,
            key=key_string
        )

print('\n✓ Тестовые данные успешно добавлены!')
