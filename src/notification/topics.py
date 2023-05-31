from notification import topic


def add_topics():
    # Notification topics
    topic.add_topic('info', type='info', message='info message')
    topic.add_topic('warning', type='warning', message='warning message')

    # Firewall topics
    topic.add_topic('log')
