from django.apps import AppConfig


class BacheConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'bache'

    def ready(self):
        import bache.signals  # 👈 Importar aquí para activar las señales