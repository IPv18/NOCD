from notification import Notification
from time import sleep


class Test(Notification):
    notification_args = {'a': 69}

    def __init__(self) -> None:
        super().__init__()

class A():
    id = 0
    def __init__(self) -> None:
        pass

    def test(self, a):
        self.id = a

def test(a):
    print(f'hello {a}')


t = Test()
a = A()

# subscribe to the Test notification
t += a.test
t += test

# simulate code running
sleep(1.0)

# id before notification is sent
print(f'a ID before: {a.id}\n')

t.send()

# id after notification is sent
print(f'a ID after: {a.id}')
