from os import environ
from django.apps import AppConfig
from notification import notification as notif


class NotificationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'notification'

    def ready(self):
        from notification import jobs
        if environ.get('RUN_MAIN', None) != 'true':
            self.add_notifications()
            if environ.get('DEBUG') == True:
                jobs.start_scheduler()

    def add_notifications(self):
        notif.add_notification('info', type='info', message='info message')
        notif.add_notification('warning', type='warning',
                               message='warning message')

        def send_notification(type, message):
            from notification.models import NotificationInfo
            notification_info = NotificationInfo(type=type, message=message)
            notification_info.save()

        notif.subscribe('info', send_notification)
        notif.subscribe('warning', send_notification)
