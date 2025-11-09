"""
Management command to generate translations using Gemini AI
Usage: python manage.py generate_translations
"""
from django.core.management.base import BaseCommand
from authentication.translation_service import GeminiTranslationService
import json
from pathlib import Path
from django.conf import settings

class Command(BaseCommand):
    help = 'Generate translations for all supported languages using Gemini AI'

    def handle(self, *args, **options):
        self.stdout.write('Starting translation generation...')
        
        service = GeminiTranslationService()
        
        if not service.model:
            self.stdout.write(self.style.ERROR('Gemini API not configured. Set GEMINI_API_KEY.'))
            return
        
        # Generate translations
        all_translations = service.generate_all_translations()
        
        # Save to JSON file
        translations_dir = settings.BASE_DIR / 'translations'
        translations_dir.mkdir(exist_ok=True)
        
        output_file = translations_dir / 'translations.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(all_translations, f, ensure_ascii=False, indent=2)
        
        self.stdout.write(self.style.SUCCESS(f'Translations saved to {output_file}'))
        self.stdout.write(self.style.SUCCESS(f'Generated translations for {len(all_translations)} languages'))
        
        # Display summary
        for lang_code, translations in all_translations.items():
            self.stdout.write(f'  - {lang_code}: {len(translations)} strings')
