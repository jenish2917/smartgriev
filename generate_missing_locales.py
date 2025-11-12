import json
import os

# Base path
base_path = r'd:\smartgrive\smartgriev\frontend\public\locales'

# Languages that need additional files
incomplete_langs = {
    'as': ['complaints', 'dashboard', 'notifications'],
    'ml': ['auth', 'complaints', 'dashboard', 'notifications'],
    'or': ['auth', 'complaints', 'dashboard', 'notifications'],
    'pa': ['auth', 'complaints', 'dashboard', 'notifications'],
    'ur': ['auth', 'complaints', 'dashboard', 'notifications'],
}

# Copy English files as base for each incomplete language
for lang, missing_files in incomplete_langs.items():
    lang_dir = os.path.join(base_path, lang)
    if not os.path.exists(lang_dir):
        os.makedirs(lang_dir)
    
    for filename in missing_files:
        src_file = os.path.join(base_path, 'en', f'{filename}.json')
        dst_file = os.path.join(lang_dir, f'{filename}.json')
        
        if os.path.exists(src_file) and not os.path.exists(dst_file):
            with open(src_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Copy the structure (keys remain in English, values will be translations)
            with open(dst_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            print(f"✓ Created {lang}/{filename}.json")

print("\nAll missing files created!")
