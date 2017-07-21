import logging

class GelfFilter(logging.Filter):
    def __init__(self):
        pass

    def filter(self, record):
        record.service = 'meanwise-api'
        return True
