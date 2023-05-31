from notification import topic
from notification import topics

from firewall import log_analyzer


def send_notification(type, message):
    from notification.models import NotificationInfo
    notification_info = NotificationInfo(type=type, message=message)
    notification_info.save()


def send_last_log():
    from notification.models import NotificationInfo
    notification_info = NotificationInfo(
        type='log', message=log_analyzer.read_last_line())
    notification_info.save()


def subscribe_topics():
    topics.add_topics()

    # Notification subscriptions
    topic.subscribe('info', send_notification)
    topic.subscribe('warning', send_notification)
    topic.subscribe('log', send_last_log)
