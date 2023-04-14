from notification import topic
from time import sleep


# Define a function to print the arguments
def print_arguments(a):
    print(a)


# Create a topic
topic.add_topic('Test', a=0)

# Subscribe to the Test topic
topic.subscribe('Test', print_arguments)

# Simulate code running
sleep(1.0)

# Send topic
topic.send('Test')

# Change the topic arguments
topic.change_topic_args('Test', a=1)

# Simulate code running
sleep(1.0)

# Send topic again
topic.send('Test')
