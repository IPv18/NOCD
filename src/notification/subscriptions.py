from notification import topic
from notification import topics


def send_notification(type, message):
    from notification.models import NotificationInfo
    notification_info = NotificationInfo(type=type, message=message)
    notification_info.save()

    topic.send('new_notifications')


def send_last_log(message):
    from notification.models import NotificationInfo
    notification_info = NotificationInfo(
        type='log', message=message)
    notification_info.save()


def subscribe_topics():
    topics.add_topics()

    # Notification subscriptions
    topic.subscribe('info', send_notification)
    topic.subscribe('warning', send_notification)
    topic.subscribe('log', send_last_log)
