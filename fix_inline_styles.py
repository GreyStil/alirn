#!/usr/bin/env python3
import os
import re

# Словарь замен для inline стилей
REPLACEMENTS = [
    # Carousel captions
    (r'<div class="carousel-caption[^"]*"[^>]*style="background-color: rgba\(0,0,0,0\.7\);">', 
     '<div class="carousel-caption d-none d-md-block carousel-caption-dark">'),
    
    # Text muted styles  
    (r'<p style="color: #999; font-size: 12px; margin-bottom: 8px;">',
     '<p class="text-muted-small">'),
    
    # Card styles
    (r'<div class="card mb-3" style="background-color: #16213e; border-color: #e94560;">',
     '<div class="card mb-3 card-highlight">'),
    
    (r'<div class="card" style="background-color: #16213e; border-color: #333;">',
     '<div class="card card-dark">'),
    
    (r'<div class="card mb-4" style="background-color: #16213e; border-color: #333;">',
     '<div class="card mb-4 card-dark">'),
    
    # Alert styles
    (r'<div class="alert alert-dark" style="word-break: break-all; font-family: monospace;">',
     '<div class="alert alert-dark alert-key">'),
    
    # Payment form
    (r'<form method="post" action="[^"]*" style="display: inline;">',
     '<form method="post" class="form-remove-inline">'),
    
    # Badges with inline colors
    (r'<span class="badge" style="background-color: #0f3460;">',
     '<span class="badge badge-platform">'),
    
    (r'<span class="badge" style="background-color: #16213e;">',
     '<span class="badge badge-genre">'),
    
    # Small text styles  
    (r'<small style="color: #999;">',
     '<small class="text-muted">'),
    
    # Payment emulate text
    (r'<p style="color: #999;">Пожалуйста, не закрывайте эту страницу</p>',
     '<p class="text-muted">Пожалуйста, не закрывайте эту страницу</p>'),
]

def fix_template_file(filepath):
    """Исправляет inline стили в файле шаблона"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        for pattern, replacement in REPLACEMENTS:
            content = re.sub(pattern, replacement, content)
        
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
            if fix_template_file(filepath):
                print(f"✓ Исправлен: {filepath}")
                fixed_count += 1
            else:
                print(f"  Не требует исправлений: {filepath}")

print(f"\n✓ Всего исправлено файлов: {fixed_count}")
