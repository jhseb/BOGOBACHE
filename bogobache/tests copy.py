import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bogobache.settings')  # ajusta al nombre real del settings.py
django.setup()

from django.utils import timezone

print("UTC:", timezone.now())