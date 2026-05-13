import os
import django
import random
from datetime import datetime, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from shop.models import Game, GameKey

# Расширенный список игр с разными жанрами, платформами и ценами
GAMES_DATA = [
    # AAA Новинки (дорогие, популярные)
    {"title": "Baldur's Gate 3", "developer": "Larian Studios", "publisher": "Larian Studios", "platform": "steam", "genre": "rpg", "region": "Global", "price": 3999.00, "discount": 0},
    {"title": "Starfield", "developer": "Bethesda", "publisher": "Microsoft", "platform": "steam", "genre": "rpg", "region": "Global", "price": 3999.00, "discount": 0},
    {"title": "Cyberpunk 2077: Phantom Liberty", "developer": "CD Projekt Red", "publisher": "CD Projekt", "platform": "steam", "genre": "action", "region": "Global", "price": 2999.00, "discount": 10},
    {"title": "Final Fantasy XVI", "developer": "Square Enix", "publisher": "Square Enix", "platform": "steam", "genre": "rpg", "region": "Global", "price": 4999.00, "discount": 0},
    {"title": "Dragon's Dogma 2", "developer": "Capcom", "publisher": "Capcom", "platform": "steam", "genre": "rpg", "region": "Global", "price": 3999.00, "discount": 15},
    {"title": "Street Fighter 6", "developer": "Capcom", "publisher": "Capcom", "platform": "steam", "genre": "fighting", "region": "Global", "price": 2999.00, "discount": 0},
    {"title": "Tekken 8", "developer": "Bandai Namco", "publisher": "Bandai Namco", "platform": "steam", "genre": "fighting", "region": "Global", "price": 2999.00, "discount": 0},
    {"title": "Alan Wake 2", "developer": "Remedy", "publisher": "Epic Games", "platform": "steam", "genre": "horror", "region": "Global", "price": 3499.00, "discount": 20},
    {"title": "Dead Space Remake", "developer": "EA Motive", "publisher": "EA", "platform": "steam", "genre": "horror", "region": "Global", "price": 2999.00, "discount": 25},
    {"title": "Forspoken", "developer": "Luminous Productions", "publisher": "Square Enix", "platform": "steam", "genre": "action", "region": "Global", "price": 2499.00, "discount": 50},
    
    # Популярные классики
    {"title": "The Witcher 3: Wild Hunt", "developer": "CD Projekt Red", "publisher": "CD Projekt", "platform": "steam", "genre": "rpg", "region": "Global", "price": 2999.00, "discount": 20},
    {"title": "Elden Ring", "developer": "FromSoftware", "publisher": "Bandai Namco", "platform": "steam", "genre": "action", "region": "Global", "price": 3999.00, "discount": 0},
    {"title": "Dark Souls III", "developer": "FromSoftware", "publisher": "Bandai Namco", "platform": "steam", "genre": "action", "region": "Global", "price": 1999.00, "discount": 15},
    {"title": "Dark Souls II", "developer": "FromSoftware", "publisher": "Bandai Namco", "platform": "steam", "genre": "action", "region": "Global", "price": 1499.00, "discount": 30},
    {"title": "Dark Souls", "developer": "FromSoftware", "publisher": "Bandai Namco", "platform": "steam", "genre": "action", "region": "Global", "price": 999.00, "discount": 40},
    {"title": "Bloodborne", "developer": "FromSoftware", "publisher": "Sony", "platform": "steam", "genre": "action", "region": "Global", "price": 1999.00, "discount": 10},
    {"title": "Sekiro: Shadows Die Twice", "developer": "FromSoftware", "publisher": "Activision", "platform": "steam", "genre": "action", "region": "Global", "price": 2499.00, "discount": 0},
    {"title": "Skyrim", "developer": "Bethesda", "publisher": "Bethesda", "platform": "steam", "genre": "rpg", "region": "Global", "price": 699.00, "discount": 60},
    {"title": "Fallout 4", "developer": "Bethesda", "publisher": "Bethesda", "platform": "steam", "genre": "rpg", "region": "Global", "price": 999.00, "discount": 50},
    {"title": "Oblivion", "developer": "Bethesda", "publisher": "Bethesda", "platform": "steam", "genre": "rpg", "region": "Global", "price": 599.00, "discount": 70},
    
    # Экшены
    {"title": "GTA V", "developer": "Rockstar", "publisher": "Rockstar", "platform": "steam", "genre": "action", "region": "Global", "price": 1999.00, "discount": 0},
    {"title": "Red Dead Redemption 2", "developer": "Rockstar", "publisher": "Rockstar", "platform": "steam", "genre": "action", "region": "Global", "price": 2499.00, "discount": 15},
    {"title": "Hogwarts Legacy", "developer": "Avalanche", "publisher": "WB Games", "platform": "steam", "genre": "action", "region": "Global", "price": 2999.00, "discount": 30},
    {"title": "Dying Light 2", "developer": "Techland", "publisher": "Techland", "platform": "steam", "genre": "horror", "region": "Global", "price": 2499.00, "discount": 25},
    {"title": "Resident Evil 4 Remake", "developer": "Capcom", "publisher": "Capcom", "platform": "steam", "genre": "horror", "region": "Global", "price": 3999.00, "discount": 0},
    {"title": "Resident Evil 8", "developer": "Capcom", "publisher": "Capcom", "platform": "steam", "genre": "horror", "region": "Global", "price": 2999.00, "discount": 20},
    {"title": "Resident Evil 7", "developer": "Capcom", "publisher": "Capcom", "platform": "steam", "genre": "horror", "region": "Global", "price": 1999.00, "discount": 30},
    {"title": "The Last of Us Part I", "developer": "Naughty Dog", "publisher": "Sony", "platform": "steam", "genre": "action", "region": "Global", "price": 3499.00, "discount": 10},
    {"title": "Uncharted 4", "developer": "Naughty Dog", "publisher": "Sony", "platform": "steam", "genre": "action", "region": "Global", "price": 2499.00, "discount": 20},
    {"title": "God of War Ragnarök", "developer": "Santa Monica", "publisher": "Sony", "platform": "steam", "genre": "action", "region": "Global", "price": 3999.00, "discount": 0},
    
    # RPG
    {"title": "Persona 5 Royal", "developer": "Atlus", "publisher": "Atlus", "platform": "steam", "genre": "rpg", "region": "Global", "price": 1999.00, "discount": 10},
    {"title": "Persona 4 Golden", "developer": "Atlus", "publisher": "Atlus", "platform": "steam", "genre": "rpg", "region": "Global", "price": 1499.00, "discount": 20},
    {"title": "Fire Emblem: Three Houses", "developer": "IS", "publisher": "Nintendo", "platform": "steam", "genre": "rpg", "region": "Global", "price": 2999.00, "discount": 0},
    {"title": "Xenoblade Chronicles 3", "developer": "Monolith", "publisher": "Nintendo", "platform": "steam", "genre": "rpg", "region": "Global", "price": 2999.00, "discount": 15},
    {"title": "Tales of Arise", "developer": "Bandai Namco", "publisher": "Bandai Namco", "platform": "steam", "genre": "rpg", "region": "Global", "price": 1999.00, "discount": 25},
    {"title": "Tales of Berseria", "developer": "Bandai Namco", "publisher": "Bandai Namco", "platform": "steam", "genre": "rpg", "region": "Global", "price": 1499.00, "discount": 35},
    {"title": "Tales of Vesperia", "developer": "Bandai Namco", "publisher": "Bandai Namco", "platform": "steam", "genre": "rpg", "region": "Global", "price": 1499.00, "discount": 30},
    {"title": "Suikoden II", "developer": "Konami", "publisher": "Konami", "platform": "steam", "genre": "rpg", "region": "Global", "price": 999.00, "discount": 40},
    {"title": "Chrono Trigger", "developer": "Square", "publisher": "Square", "platform": "steam", "genre": "rpg", "region": "Global", "price": 1499.00, "discount": 20},
    {"title": "Final Fantasy VII", "developer": "Square", "publisher": "Square", "platform": "steam", "genre": "rpg", "region": "Global", "price": 2999.00, "discount": 0},
    
    # Стратегии
    {"title": "Civilization VI", "developer": "Firaxis", "publisher": "2K Games", "platform": "steam", "genre": "strategy", "region": "Global", "price": 1999.00, "discount": 40},
    {"title": "Total War: Warhammer III", "developer": "Creative Assembly", "publisher": "Sega", "platform": "steam", "genre": "strategy", "region": "Global", "price": 2999.00, "discount": 30},
    {"title": "StarCraft II", "developer": "Blizzard", "publisher": "Blizzard", "platform": "steam", "genre": "strategy", "region": "Global", "price": 0.00, "discount": 0},
    {"title": "Warcraft III: Reforged", "developer": "Blizzard", "publisher": "Blizzard", "platform": "steam", "genre": "strategy", "region": "Global", "price": 999.00, "discount": 50},
    {"title": "Age of Empires IV", "developer": "Relic", "publisher": "Xbox", "platform": "steam", "genre": "strategy", "region": "Global", "price": 1999.00, "discount": 35},
    {"title": "Company of Heroes 3", "developer": "Relic", "publisher": "Sega", "platform": "steam", "genre": "strategy", "region": "Global", "price": 1999.00, "discount": 25},
    {"title": "Crusader Kings III", "developer": "Paradox", "publisher": "Paradox", "platform": "steam", "genre": "strategy", "region": "Global", "price": 1999.00, "discount": 20},
    {"title": "Europa Universalis IV", "developer": "Paradox", "publisher": "Paradox", "platform": "steam", "genre": "strategy", "region": "Global", "price": 1999.00, "discount": 25},
    {"title": "Hearts of Iron IV", "developer": "Paradox", "publisher": "Paradox", "platform": "steam", "genre": "strategy", "region": "Global", "price": 1999.00, "discount": 30},
    {"title": "Stellaris", "developer": "Paradox", "publisher": "Paradox", "platform": "steam", "genre": "strategy", "region": "Global", "price": 1999.00, "discount": 35},
    
    # Puzzle & Casual
    {"title": "Portal 2", "developer": "Valve", "publisher": "Valve", "platform": "steam", "genre": "puzzle", "region": "Global", "price": 799.00, "discount": 50},
    {"title": "Portal", "developer": "Valve", "publisher": "Valve", "platform": "steam", "genre": "puzzle", "region": "Global", "price": 599.00, "discount": 60},
    {"title": "The Witness", "developer": "Thekla", "publisher": "Thekla", "platform": "steam", "genre": "puzzle", "region": "Global", "price": 1999.00, "discount": 20},
    {"title": "Tetris Effect", "developer": "Monstars", "publisher": "Monstars", "platform": "steam", "genre": "puzzle", "region": "Global", "price": 1999.00, "discount": 25},
    {"title": "The Talos Principle", "developer": "Croteam", "publisher": "Devolver", "platform": "steam", "genre": "puzzle", "region": "Global", "price": 1499.00, "discount": 30},
    {"title": "Baba Is You", "developer": "Arvi", "publisher": "Devolver", "platform": "steam", "genre": "puzzle", "region": "Global", "price": 599.00, "discount": 20},
    {"title": "Opus Magnum", "developer": "Zachtronics", "publisher": "Zachtronics", "platform": "steam", "genre": "puzzle", "region": "Global", "price": 599.00, "discount": 25},
    {"title": "Stray", "developer": "BlueTwelve", "publisher": "Annapurna", "platform": "steam", "genre": "puzzle", "region": "Global", "price": 1499.00, "discount": 20},
    {"title": "Outer Wilds", "developer": "Mobius", "publisher": "Annapurna", "platform": "steam", "genre": "puzzle", "region": "Global", "price": 1999.00, "discount": 0},
    {"title": "The Stanley Parable", "developer": "Davey", "publisher": "Davey", "platform": "steam", "genre": "puzzle", "region": "Global", "price": 599.00, "discount": 40},
    
    # Инди игры (доступные, разнообразные)
    {"title": "Hollow Knight", "developer": "Team Cherry", "publisher": "Team Cherry", "platform": "steam", "genre": "action", "region": "Global", "price": 499.00, "discount": 15},
    {"title": "Celeste", "developer": "Maddy Makes Games", "publisher": "Maddy Makes Games", "platform": "steam", "genre": "action", "region": "Global", "price": 299.00, "discount": 20},
    {"title": "Terraria", "developer": "Re-Logic", "publisher": "Re-Logic", "platform": "steam", "genre": "action", "region": "Global", "price": 399.00, "discount": 30},
    {"title": "Stardew Valley", "developer": "ConcernedApe", "publisher": "ConcernedApe", "platform": "steam", "genre": "rpg", "region": "Global", "price": 699.00, "discount": 10},
    {"title": "Hades", "developer": "Supergiant", "publisher": "Supergiant", "platform": "steam", "genre": "action", "region": "Global", "price": 1499.00, "discount": 0},
    {"title": "Hadès 2", "developer": "Supergiant", "publisher": "Supergiant", "platform": "steam", "genre": "action", "region": "Global", "price": 1999.00, "discount": 0},
    {"title": "Synthetik", "developer": "Flow Fire", "publisher": "Flow Fire", "platform": "steam", "genre": "action", "region": "Global", "price": 499.00, "discount": 40},
    {"title": "Binding of Isaac", "developer": "Nicalis", "publisher": "Nicalis", "platform": "steam", "genre": "action", "region": "Global", "price": 599.00, "discount": 25},
    {"title": "Nuclear Throne", "developer": "Vlambeer", "publisher": "Vlambeer", "platform": "steam", "genre": "action", "region": "Global", "price": 499.00, "discount": 35},
    {"title": "Spelunky 2", "developer": "Mossmouth", "publisher": "Mossmouth", "platform": "steam", "genre": "action", "region": "Global", "price": 999.00, "discount": 20},
    
    # Шутеры
    {"title": "Counter-Strike 2", "developer": "Valve", "publisher": "Valve", "platform": "steam", "genre": "shooter", "region": "Global", "price": 0.00, "discount": 0},
    {"title": "Valorant", "developer": "Riot Games", "publisher": "Riot Games", "platform": "steam", "genre": "shooter", "region": "Global", "price": 0.00, "discount": 0},
    {"title": "Destiny 2", "developer": "Bungie", "publisher": "Bungie", "platform": "steam", "genre": "shooter", "region": "Global", "price": 0.00, "discount": 0},
    {"title": "Halo Infinite", "developer": "343i", "publisher": "Xbox", "platform": "steam", "genre": "shooter", "region": "Global", "price": 0.00, "discount": 0},
    {"title": "Call of Duty Modern Warfare III", "developer": "Infinity Ward", "publisher": "Activision", "platform": "steam", "genre": "shooter", "region": "Global", "price": 3999.00, "discount": 0},
    {"title": "Call of Duty Modern Warfare II", "developer": "Infinity Ward", "publisher": "Activision", "platform": "steam", "genre": "shooter", "region": "Global", "price": 2999.00, "discount": 20},
    {"title": "Overwatch 2", "developer": "Blizzard", "publisher": "Blizzard", "platform": "steam", "genre": "shooter", "region": "Global", "price": 0.00, "discount": 0},
    {"title": "Team Fortress 2", "developer": "Valve", "publisher": "Valve", "platform": "steam", "genre": "shooter", "region": "Global", "price": 0.00, "discount": 0},
    {"title": "Apex Legends", "developer": "Respawn", "publisher": "EA", "platform": "steam", "genre": "shooter", "region": "Global", "price": 0.00, "discount": 0},
    {"title": "Fortnite", "developer": "Epic Games", "publisher": "Epic Games", "platform": "steam", "genre": "shooter", "region": "Global", "price": 0.00, "discount": 0},
    
    # Спортивные и гоночные
    {"title": "F1 23", "developer": "Codemasters", "publisher": "EA", "platform": "steam", "genre": "sports", "region": "Global", "price": 2999.00, "discount": 25},
    {"title": "FIFA 24", "developer": "EA Sports", "publisher": "EA", "platform": "steam", "genre": "sports", "region": "Global", "price": 3999.00, "discount": 0},
    {"title": "NBA 2K24", "developer": "2K Sports", "publisher": "2K", "platform": "steam", "genre": "sports", "region": "Global", "price": 3999.00, "discount": 10},
    {"title": "Madden NFL 24", "developer": "EA Sports", "publisher": "EA", "platform": "steam", "genre": "sports", "region": "Global", "price": 3999.00, "discount": 15},
    {"title": "Need for Speed Unbound", "developer": "Ghost", "publisher": "EA", "platform": "steam", "genre": "sports", "region": "Global", "price": 2999.00, "discount": 30},
    {"title": "Need for Speed Heat", "developer": "Ghost", "publisher": "EA", "platform": "steam", "genre": "sports", "region": "Global", "price": 1999.00, "discount": 40},
    {"title": "Forza Horizon 5", "developer": "Playground", "publisher": "Xbox", "platform": "steam", "genre": "sports", "region": "Global", "price": 2999.00, "discount": 35},
    {"title": "Forza Motorsport 8", "developer": "Turn 10", "publisher": "Xbox", "platform": "steam", "genre": "sports", "region": "Global", "price": 2999.00, "discount": 20},
    {"title": "Gran Turismo Sport", "developer": "Polyphony", "publisher": "Sony", "platform": "steam", "genre": "sports", "region": "Global", "price": 1999.00, "discount": 25},
    {"title": "iRacing", "developer": "iRacing", "publisher": "iRacing", "platform": "steam", "genre": "sports", "region": "Global", "price": 1499.00, "discount": 0},
]

# Расширенный список для достижения 1000 игр
ADDITIONAL_GAMES = []

# Добавим инди/популярные игры
indie_games = [
    ("A Short Hike", "adamgryu", "adamgryu", "rpg", 349.00, 15),
    ("Valheim", "Iron Gate", "Iron Gate", "action", 449.00, 10),
    ("V Rising", "Stunlock Studios", "Stunlock", "rpg", 1999.00, 0),
    ("Grounded", "Obsidian", "Xbox", "action", 1999.00, 20),
    ("Palworld", "Pocketpair", "Pocketpair", "rpg", 2999.00, 0),
    ("Satisfactory", "Coffee Stain", "Coffee Stain", "strategy", 1999.00, 15),
    ("Core Keeper", "Pugstorm", "Pugstorm", "action", 299.00, 25),
    ("Dredge", "Team17", "Team17", "horror", 1299.00, 10),
    ("Echoes of Wisdom", "Nintendo", "Nintendo", "rpg", 2999.00, 0),
    ("Dave the Diver", "Nexon", "Nexon", "puzzle", 299.00, 0),
    ("Kentucky Route Zero", "Cardboard", "Cardboard", "action", 1499.00, 0),
    ("Return of the Obra Dinn", "Lucas", "Lucas", "puzzle", 999.00, 0),
    ("The Night Fisherman", "Goloso", "Goloso", "rpg", 399.00, 10),
    ("Subnautica", "Unknown", "Unknown", "action", 1999.00, 30),
    ("Raft", "Redbeet", "Redbeet", "action", 1999.00, 15),
]

for title, dev, pub, genre, price, discount in indie_games:
    ADDITIONAL_GAMES.append({
        "title": title, "developer": dev, "publisher": pub,
        "platform": "steam", "genre": genre, "region": "Global",
        "price": price, "discount": discount
    })

# Мультиплеерные и браузер-игры
multiplayer_games = [
    ("Rust", "Facepunch", "Facepunch", "action", 1999.00, 0),
    ("ARK: Survival Evolved", "Studio Wildcard", "Studio", "action", 999.00, 50),
    ("Conan Exiles", "Funcom", "Funcom", "rpg", 999.00, 40),
    ("7 Days to Die", "Fun Pimps", "Fun Pimps", "action", 1499.00, 20),
    ("Minecraft", "Mojang", "Microsoft", "action", 2699.00, 10),
    ("Don't Starve Together", "Klei", "Klei", "action", 599.00, 30),
    ("Grounded", "Obsidian", "Xbox", "action", 1999.00, 25),
]

for title, dev, pub, genre, price, discount in multiplayer_games:
    if not any(g["title"] == title for g in GAMES_DATA + ADDITIONAL_GAMES):
        ADDITIONAL_GAMES.append({
            "title": title, "developer": dev, "publisher": pub,
            "platform": "steam", "genre": genre, "region": "Global",
            "price": price, "discount": discount
        })

# Генерируем оставшиеся игры случайно
GAME_TITLES = [
    "Mystic Quest", "Shadow Realm", "Divine Conquest", "Eternal Odyssey",
    "Nexus Empire", "Void Walker", "Time Paradox", "Lost Dimension",
    "Solar Flare", "Cosmic Drift", "Atlantica Online", "World of Magic",
    "Dungeons Unlimited", "Battle Royale", "Survival Mode", "Classic RPG",
    "Modern Warfare", "Ancient Mystery", "Future Tech", "Cyber Matrix",
    "Digital Dreams", "Virtual Reality", "Augmented World", "Space Opera",
]

STUDIOS = [
    "Indie Studio", "AAA Developer", "Mobile Games", "VR Specialists",
    "EA Sports", "Ubisoft", "Activision", "Take-Two", "Sony", "Nintendo",
    "Microsoft", "Square Enix", "Bandai Namco", "Capcom", "Sega",
]

genres_list = ["rpg", "action", "strategy", "puzzle", "shooter", "sports", "horror", "fighting"]
price_ranges = [(299, 699), (699, 1499), (1499, 1999), (1999, 2999), (2999, 3999), (3999, 4999)]

# Генерируем недостающие игры
current_count = len(GAMES_DATA) + len(ADDITIONAL_GAMES)
for i in range(1000 - current_count):
    title = f"{random.choice(GAME_TITLES)} {i+1}"
    dev = random.choice(STUDIOS)
    pub = random.choice(STUDIOS)
    genre = random.choice(genres_list)
    price_range = random.choice(price_ranges)
    price = random.uniform(price_range[0], price_range[1])
    discount = random.choice([0, 5, 10, 15, 20, 25, 30, 35, 40, 50])
    
    ADDITIONAL_GAMES.append({
        "title": title, "developer": dev, "publisher": pub,
        "platform": "steam", "genre": genre, "region": "Global",
        "price": price, "discount": discount
    })

ALL_GAMES = GAMES_DATA + ADDITIONAL_GAMES

print(f"Всего игр для загрузки: {len(ALL_GAMES)}")

# Удаляем старые данные (в порядке зависимостей)
from shop.models import Order, Cart, Review, BalanceTopUp, UserProfile

Order.objects.all().delete()
Review.objects.all().delete()
Cart.objects.all().delete()
GameKey.objects.all().delete()
Game.objects.all().delete()

# Загружаем новые игры и ключи
for idx, game_data in enumerate(ALL_GAMES):
    # Генерируем дату выпуска в прошлом
    days_ago = random.randint(1, 3650)  # от 1 до 10 лет назад
    release_date = datetime.now() - timedelta(days=days_ago)
    
    game = Game.objects.create(
        title=game_data["title"],
        description=f"Описание игры {game_data['title']}. Разработана студией {game_data['developer']}. " +
                   f"Издана компанией {game_data['publisher']}. Жанр: {game_data['genre'].upper()}",
        developer=game_data["developer"],
        publisher=game_data["publisher"],
        platform=game_data["platform"],
        genre=game_data["genre"],
        region=game_data["region"],
        price=game_data["price"],
        discount_percent=game_data["discount"],
        release_date=release_date.date(),
        system_requirements="OS: Windows 7+ / macOS 10.7+ / Linux\nCPU: Dual Core 2.0 GHz\nRAM: 2 GB\nGPU: Integrated Graphics\nStorage: 5-10 GB",
    )
    
    # Создаём 10 ключей для каждой игры
    for key_idx in range(10):
        key_base = f"{str(idx+1).zfill(4)}-{str(key_idx+1).zfill(4)}"
        key = f"{key_base}-XXXX-XXXX-{game_data['title'][:3].upper()}"
        GameKey.objects.create(game=game, key=key)
    
    if (idx + 1) % 100 == 0:
        print(f"Загружено {idx + 1} игр...")

print(f"✓ Успешно загружено {len(ALL_GAMES)} игр с ключами!")
print(f"✓ Всего создано ключей: {len(ALL_GAMES) * 10}")
