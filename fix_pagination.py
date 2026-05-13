#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import re

templates_dir = 'templates'
files_to_fix = [
    'shop/catalog.html',
    'shop/search.html',
    'accounts/profile_balance.html',
    'accounts/profile_orders.html',
    'accounts/profile_library.html',
    'accounts/profile_favorites.html',
]

for file_path in files_to_fix:
    full_path = os.path.join(templates_dir, file_path)
    if not os.path.exists(full_path):
        print(f"❌ Файл не найден: {full_path}")
        continue
    
    with open(full_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Fix pagination whitespace
    # Pattern: <ul class="pagination ...> followed by whitespace and {% if/{% for
    content = re.sub(
        r'(<ul[^>]*class="[^"]*pagination[^"]*"[^>]*>)\s+({%)',
        r'\1\2',
        content
    )
    
    # Fix: {% endif %} or {% endfor %} followed by whitespace and </ul>
    content = re.sub(
        r'({%\s+end\w+\s+%})\s+(</ul>)',
        r'\1\2',
        content
    )
    
    # Add {%- for if blocks inside ul
    content = re.sub(
        r'(<ul[^>]*class="[^"]*pagination[^"]*"[^>]*>)\s+({%\s+if\s+)',
        r'\1\n                    {%- if ',
        content
    )
    
    # Fix {% if %} to {%- if %} inside pagination
    content = re.sub(
        r'(pagination[^>]*>)\s+({%\s+if\s+)',
        r'\1\n                    {%- if ',
        content
    )
    
    with open(full_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✓ Исправлен: {file_path}")

print("\n✓ Готово!")
