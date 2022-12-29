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

        if (not callable(subscriber_method)):
            raise Exception('Argument provided is not a function')

        if (list(self.notification_args.keys()) != inspect.getfullargspec(subscriber_method).args):
            raise Exception(
                'Method provided does not contain matching arguments')

        self.subscriber_methods.append(subscriber_method)

        return self
