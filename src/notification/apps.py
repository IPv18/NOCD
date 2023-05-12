from os import environ
from django.apps import AppConfig
from django.conf import settings
from notification import topic


class NotificationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'notification'

    def ready(self):
        try:
            from notification import jobs
            if environ.get('RUN_MAIN', None) != 'true':
                self.add_topics()
                if settings.DEBUG:
                    jobs.start_scheduler()
        except Exception as e:
            print(e)

    def add_topics(self):
        topic.add_topic('info', type='info', message='info message')
        topic.add_topic('warning', type='warning', message='warning message')

        def send_notification(type, message):
            from notification.models import NotificationInfo
            notification_info = NotificationInfo(type=type, message=message)
            notification_info.save()

        topic.subscribe('info', send_notification)
        topic.subscribe('warning', send_notification)
