from django.apps import AppConfig


class NetworkSnifferConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'network_sniffer'

    def ready(self):
        from .network_sniffer import main
        main()