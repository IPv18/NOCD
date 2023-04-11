import inspect


notifications = {}


def add_notification(notification, **kwargs):
    '''
    Add a notification with arguments
    '''

    if notification in notifications:
        raise Exception('Notification already exists')

    notifications[notification] = {
        'notification_args': kwargs,
        'subscriber_methods': []
    }


def change_notification_args(notification, **kwargs):
    '''
    Change the notification arguments
    '''

    if notification not in notifications:
        raise Exception('Notification does not exist')

    notifications[notification]['notification_args'] = kwargs


def subscribe(notification, subscriber_method):
    '''
    Adds function to notification
    '''

    # Check if the argument is callable
    if not callable(subscriber_method):
        raise Exception('Argument provided is not a function')

    # Get the method arguments

    args = inspect.getfullargspec(subscriber_method).args
    # Skip self if found
    if '.' in subscriber_method.__qualname__ and args[0] == 'self':
        args = args[1:]

    # Check if the notification exists
    if notification not in notifications:
        notifications[notification] = {
            'notification_args': {},
            'subscriber_methods': []
        }

    # Check if the arguments match with the notification arguments
    notification_args = notifications[notification]['notification_args']
    if list(notification_args.keys()) != args:
        raise Exception(
            'Method provided does not contain matching arguments')

    notifications[notification]['subscriber_methods'].append(subscriber_method)


def send(notification):
    '''
    Call all the methods from the subscribers
    '''

    if notification not in notifications:
        raise Exception('Notification does not exist')

    notification_args = notifications[notification]['notification_args']
    subscriber_methods = notifications[notification]['subscriber_methods']

    for subscriber_method in subscriber_methods:
        subscriber_method(**notification_args)
