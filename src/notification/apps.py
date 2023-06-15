from os import environ
from django.apps import AppConfig
from django.conf import settings
from notification import subscriptions


class NotificationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'notification'

    def ready(self):
        try:
            from notification import jobs
            if environ.get('RUN_MAIN', None) != 'true':
                subscriptions.subscribe_topics()
                if settings.DEBUG:
                    jobs.start_scheduler()
        except Exception as e:
            print("Notifications initialization error:")
            print(e)
