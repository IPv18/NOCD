from notification import Notification
from time import sleep


class Test(Notification):
    notification_args = {'a': 69}

    def __init__(self) -> None:
        super().__init__()


def test(a):
    print(a)


t = Test()
t += test

sleep(1.0)

t.send()
