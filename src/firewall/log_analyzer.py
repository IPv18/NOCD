LOG_FILE_PATH = '/var/log/messages'


def read_last_line():
    with open(LOG_FILE_PATH, 'r') as file:
        lines = file.readlines()
        if lines:
            last_line = lines[-1].strip()
            return last_line
        else:
            return "The log file is empty."
