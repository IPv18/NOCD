import inspect


topics = {}


def add_topic(topic, **kwargs):
    '''
    Add a topic with arguments
    '''

    if topic in topics:
        raise Exception('Topic already exists')

    topics[topic] = {
        'topic_args': kwargs,
        'subscriber_methods': []
    }


def change_topic_args(topic, **kwargs):
    '''
    Change the topic arguments
    '''

    if topic not in topics:
        raise Exception('Topic does not exist')

    topics[topic]['topic_args'] = kwargs


def subscribe(topic, subscriber_method, **kwargs):
    '''
    Add a function to topic
    '''

    # Check if the topic exists
    if topic not in topics:
        raise Exception('Topic does not exist')

    # Check if the argument is callable
    if not callable(subscriber_method):
        raise Exception('Argument provided is not a function')

    # Get the method arguments
    args = inspect.getfullargspec(subscriber_method).args

    # Skip self if found
    if hasattr(callable, '__self__') and len(args) > 0 and args[0] == "self":
        args = args[1:]

    # Check if the arguments match with the topic arguments
    topic_args = topics[topic]['topic_args']
    if list(topic_args.keys()) != args:
        raise Exception(
            'Method provided does not contain matching arguments')

    topics[topic]['subscriber_methods'].append({
        'method': subscriber_method,
        'extra_args': kwargs
    })


def unsubscribe(topic, subscriber_method):
    '''
    Remove a function from topic
    '''

    if topic not in topics:
        raise Exception('Topic does not exist')

    if subscriber_method not in topics[topic]['subscriber_methods']:
        raise Exception('Method is not subscribed to topic')
    
    for subscriber_method in topics[topic]['subscriber_methods']:
        if subscriber_method['method'] == subscriber_method:
            topics[topic]['subscriber_methods'].remove(subscriber_method)
            break


def send(topic):
    '''
    Call all the methods from the subscribers
    '''

    if topic not in topics:
        raise Exception('Topic does not exist')

    topic_args = topics[topic]['topic_args']
    subscriber_methods = topics[topic]['subscriber_methods']

    for subscriber_method in subscriber_methods:
        subscriber_method['method'](**topic_args, **subscriber_method['extra_args'])


def send(topic, **kwargs):
    '''
    Call all the methods from the subscribers with custom arguments
    '''

    if topic not in topics:
        raise Exception('Topic does not exist')

    subscriber_methods = topics[topic]['subscriber_methods']

    for subscriber_method in subscriber_methods:
        args = inspect.getfullargspec(subscriber_method['method']).args

        # Skip self if found
        if hasattr(callable, '__self__') and len(args) > 0 and args[0] == "self":
            args = args[1:]

        # Check if the arguments match with the topic arguments
        if list(kwargs.keys()) != args:
            raise Exception(
                'Method provided does not contain matching arguments')

        subscriber_method['method'](**kwargs, **subscriber_method['extra_args'])
