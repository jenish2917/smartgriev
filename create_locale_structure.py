#!/usr/bin/env python3
import json
import os

base_path = r'd:\smartgrive\smartgriev\frontend\public\locales'

# Since manual translation is best, we'll copy English for now with a note
# In production, these should be professionally translated

# For Odia (or), Punjabi (pa), Urdu (ur) - copy English structure
# This ensures all keys are available, translations can be added later
copy_langs = ['or', 'pa', 'ur']

for lang in copy_langs:
    for namespace in ['auth', 'complaints', 'dashboard', 'notifications']:
        src = os.path.join(base_path, 'en', f'{namespace}.json')
        dst = os.path.join(base_path, lang, f'{namespace}.json')
        
        if os.path.exists(src) and not os.path.exists(dst):
            with open(src, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            with open(dst, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            print(f"Created {lang}/{namespace}.json")

print("\nAll locale files created successfully!")
print("\nNote: Translations in or/*, pa/*, and ml/{complaints,dashboard,notifications}.json")
print("use English as placeholders. These should be professionally translated.")
