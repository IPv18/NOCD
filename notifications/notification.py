from abc import ABC, abstractmethod
import inspect


class Notification(ABC):
    notification_args = {}

    def __init__(self) -> None:
        self.subscriber_methods = []
        super().__init__()

    def send(self):
        '''
        Call all the methods from the subscribers
        '''

        for subscriber_method in self.subscriber_methods:
            subscriber_method(**self.notification_args)

    def __iadd__(self, subscriber_method):
        '''
        Overload '+=' as a subscription method
        '''
        
        # Check if the argument is callable
        if not callable(subscriber_method):
            raise Exception('Argument provided is not a function')

        # Get the method arguments
        args = inspect.getfullargspec(subscriber_method).args

        # Skip self if found
        if '.' in subscriber_method.__qualname__ and args[0] == 'self':
            args = args[1:]

        # Check if the arguments match with the notification arguments
        if list(self.notification_args.keys()) != args:
            raise Exception(
                'Method provided does not contain matching arguments')

        self.subscriber_methods.append(subscriber_method)

        return self
