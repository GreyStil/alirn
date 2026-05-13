#!/usr/bin/env python3
import os
import re

def fix_select_accessibility(filepath):
    """Добавляет aria-label к select элементам"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Добавляем aria-label к select элементам из catalog.html
        content = re.sub(
            r'<select name="genre" class="form-select">',
            '<select name="genre" class="form-select" aria-label="Filter by genre">',
            content
        )
        
        content = re.sub(
            r'<select name="platform" class="form-select">',
            '<select name="platform" class="form-select" aria-label="Filter by platform">',
            content
        )
        
        content = re.sub(
            r'<select name="sort" class="form-select">',
            '<select name="sort" class="form-select" aria-label="Sort games">',
            content
        )
        
        content = re.sub(
            r'<select name="rating" class="form-select">',
            '<select name="rating" class="form-select" aria-label="Select rating">',
            content
        )
        
        if content != original_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        return False
    except Exception as e:
        print(f"Ошибка при обработке {filepath}: {e}")
        return False

# Ищем все HTML файлы в шаблонах
templates_dir = 'templates'
fixed_count = 0

for root, dirs, files in os.walk(templates_dir):
    for file in files:
        if file.endswith('.html'):
            filepath = os.path.join(root, file)
            if fix_select_accessibility(filepath):
                print(f"✓ Добавлены aria-label в: {filepath}")
                fixed_count += 1

print(f"\n✓ Всего исправлено файлов: {fixed_count}")
