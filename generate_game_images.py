import os
import django
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import random
import colorsys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from shop.models import Game

# Цвета для игр в зависимости от жанра
GENRE_COLORS = {
    'rpg': [(75, 0, 130), (128, 0, 128)],  # Индиго, Пурпур
    'action': [(220, 20, 60), (255, 69, 0)],  # Алый, Красно-оранжевый
    'strategy': [(0, 100, 0), (34, 139, 34)],  # Тёмно-зелёный
    'puzzle': [(30, 144, 255), (0, 191, 255)],  # Додж блюе
    'shooter': [(128, 128, 0), (184, 134, 11)],  # Оливковый
    'sports': [(255, 165, 0), (255, 140, 0)],  # Оранжевый
    'horror': [(25, 25, 112), (47, 79, 79)],  # Полуночно-синий
    'fighting': [(180, 82, 45), (205, 92, 92)],  # Коричневый
}

def get_genre_colors(genre):
    """Получить цвета для жанра"""
    return GENRE_COLORS.get(genre, [(100, 100, 100), (150, 150, 150)])

def create_cover_image(game_id, title, genre):
    """Создать обложку игры (400x500)"""
    width, height = 400, 500
    colors = get_genre_colors(genre)
    
    # Создаём изображение с градиентом
    img = Image.new('RGB', (width, height), colors[0])
    pixels = img.load()
    
    # Добавляем диагональный градиент
    for y in range(height):
        for x in range(width):
            ratio = (x + y) / (width + height)
            r = int(colors[0][0] * (1 - ratio) + colors[1][0] * ratio)
            g = int(colors[0][1] * (1 - ratio) + colors[1][1] * ratio)
            b = int(colors[0][2] * (1 - ratio) + colors[1][2] * ratio)
            pixels[x, y] = (r, g, b)
    
    # Добавляем текст
    draw = ImageDraw.Draw(img)
    
    # Эффект тени для текста
    try:
        font_large = ImageFont.truetype("arial.ttf", 28)
        font_small = ImageFont.truetype("arial.ttf", 12)
    except:
        font_large = ImageFont.load_default()
        font_small = ImageFont.load_default()
    
    # Рисуем название игры по центру
    title_lines = []
    words = title.split()
    current_line = ""
    for word in words:
        if len(current_line + word) > 20:
            title_lines.append(current_line.strip())
            current_line = word
        else:
            current_line += " " + word if current_line else word
    if current_line:
        title_lines.append(current_line)
    
    y_offset = (height - len(title_lines) * 40) // 2
    for i, line in enumerate(title_lines):
        y_pos = y_offset + i * 40
        # Тень
        draw.text((52, y_pos + 2), line, fill=(0, 0, 0), font=font_large)
        # Текст
        draw.text((50, y_pos), line, fill=(255, 255, 255), font=font_large)
    
    # Добавляем жанр внизу
    genre_text = f"🎮 {genre.upper()}"
    draw.text((10, height - 35), genre_text, fill=(200, 200, 200), font=font_small)
    
    # Добавляем ID внизу справа
    draw.text((width - 50, height - 35), f"#{game_id}", fill=(200, 200, 200), font=font_small)
    
    # Добавляем геймплейный эффект (полупрозрачная сетка)
    for x in range(0, width, 50):
        draw.line([(x, 0), (x, height)], fill=(255, 255, 255, 30), width=1)
    for y in range(0, height, 50):
        draw.line([(0, y), (width, y)], fill=(255, 255, 255, 30), width=1)
    
    # Применяем небольшую размытие
    img = img.filter(ImageFilter.GaussianBlur(radius=1))
    
    return img

def create_screenshot_image(game_id, title, screenshot_num, genre):
    """Создать скриншот игры (800x600)"""
    width, height = 800, 600
    colors = get_genre_colors(genre)
    
    # Создаём изображение с более сложной текстурой
    img = Image.new('RGB', (width, height), colors[0])
    pixels = img.load()
    
    # Добавляем случайный эффект текстуры/шума
    for y in range(height):
        for x in range(width):
            # Базовый градиент
            ratio = (x * 0.7 + y * 0.3) / (width + height)
            r = int(colors[0][0] * (1 - ratio) + colors[1][0] * ratio)
            g = int(colors[0][1] * (1 - ratio) + colors[1][1] * ratio)
            b = int(colors[0][2] * (1 - ratio) + colors[1][2] * ratio)
            
            # Добавляем шум
            noise = random.randint(-10, 10)
            pixels[x, y] = (
                max(0, min(255, r + noise)),
                max(0, min(255, g + noise)),
                max(0, min(255, b + noise))
            )
    
    draw = ImageDraw.Draw(img)
    
    try:
        font_large = ImageFont.truetype("arial.ttf", 48)
        font_small = ImageFont.truetype("arial.ttf", 20)
    except:
        font_large = ImageFont.load_default()
        font_small = ImageFont.load_default()
    
    # Добавляем текст скриншота
    text = f"Screenshot {screenshot_num}"
    draw.text((50, 250), text, fill=(255, 255, 255), font=font_large)
    draw.text((50, 320), title, fill=(200, 200, 255), font=font_small)
    
    # Добавляем элементы UI (имитация игровых элементов)
    # Здоровье/энергия на верху
    draw.rectangle([50, 30, 300, 60], outline=(0, 255, 0), width=2)
    draw.rectangle([50, 30, 250, 60], fill=(0, 255, 0))
    draw.text((310, 35), "HP: 100/100", fill=(0, 255, 0), font=font_small)
    
    # Мана на верху справа
    draw.rectangle([width - 300, 30, width - 50, 60], outline=(0, 100, 255), width=2)
    draw.rectangle([width - 300, 30, width - 150, 60], fill=(0, 100, 255))
    draw.text((width - 140, 35), "MANA: 50/50", fill=(0, 100, 255), font=font_small)
    
    # Компас внизу справа
    cx, cy = width - 100, height - 100
    radius = 40
    draw.ellipse([cx - radius, cy - radius, cx + radius, cy + radius], 
                 outline=(255, 255, 0), width=2)
    draw.line([(cx, cy - radius), (cx, cy)], fill=(255, 0, 0), width=3)  # N
    draw.line([(cx, cy), (cx + radius, cy)], fill=(100, 100, 100), width=2)  # E
    
    # Координаты внизу слева
    draw.text((50, height - 80), f"Location: Game Area #{screenshot_num}", 
             fill=(200, 200, 200), font=font_small)
    
    # Применяем размытие
    img = img.filter(ImageFilter.GaussianBlur(radius=1))
    
    return img

print("Начинаю генерацию изображений для всех игр...")
print("=" * 60)

media_path = 'media'
covers_path = os.path.join(media_path, 'games', 'covers')
screenshots_path = os.path.join(media_path, 'games', 'screenshots')

# Создаём папки если их нет
os.makedirs(covers_path, exist_ok=True)
os.makedirs(screenshots_path, exist_ok=True)

games = Game.objects.all()
total_games = games.count()

for idx, game in enumerate(games, 1):
    # Создаём обложку
    cover_img = create_cover_image(game.id, game.title, game.genre)
    cover_path = os.path.join(covers_path, f'game_{game.id}_cover.jpg')
    cover_img.save(cover_path, 'JPEG', quality=85)
    
    # Обновляем модель с путём к изображению
    game.image = f'games/covers/game_{game.id}_cover.jpg'
    game.cover_image = f'games/covers/game_{game.id}_cover.jpg'
    
    # Создаём скриншоты (3 штуки на каждую игру)
    screenshots = []
    for screenshot_num in range(1, 4):
        screenshot_img = create_screenshot_image(game.id, game.title, screenshot_num, game.genre)
        screenshot_path = os.path.join(
            screenshots_path, 
            f'game_{game.id}_screenshot_{screenshot_num}.jpg'
        )
        screenshot_img.save(screenshot_path, 'JPEG', quality=80)
        screenshots.append(f'games/screenshots/game_{game.id}_screenshot_{screenshot_num}.jpg')
    
    game.save()
    
    if idx % 50 == 0:
        print(f"✓ Обработано {idx}/{total_games} игр ({idx*100//total_games}%)")

print("=" * 60)
print(f"✓ Успешно сгенерировано {total_games} обложек!")
print(f"✓ Успешно сгенерировано {total_games * 3} скриншотов!")
print(f"✓ Все изображения сохранены в {media_path}/games/")
