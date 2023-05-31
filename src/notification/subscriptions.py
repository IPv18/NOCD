from notification import topic
from notification.topics import add_topics


def send_notification(type, message):
    from notification.models import NotificationInfo
    notification_info = NotificationInfo(type=type, message=message)
    notification_info.save()


def send_last_log():
    from firewall.log_analyzer import read_last_line
    from notification.models import NotificationInfo
    notification_info = NotificationInfo(type='log', message=read_last_line())
    notification_info.save()


def subscribe_topics():
    # Notification subscriptions
    topic.subscribe('info', send_notification)
    topic.subscribe('warning', send_notification)
    topic.subscribe('log', send_last_log)


add_topics()
