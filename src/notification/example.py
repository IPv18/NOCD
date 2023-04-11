import notification as notif
from time import sleep


# Define a function to print the arguments
def print_arguments(a):
    print(a)


# Create a notification
notif.add_notification('Test', a=0)

# Subscribe to the Test notification
notif.subscribe('Test', print_arguments)

# Simulate code running
sleep(1.0)

# Send notification
notif.send('Test')

# Change the notification arguments
notif.change_notification_args('Test', a=1)

# Simulate code running
sleep(1.0)

# Send notification again
notif.send('Test')
