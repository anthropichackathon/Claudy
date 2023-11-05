import logging

from src.utils.text_handler import TextHandler


class SingletonType(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(SingletonType, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class Logger:
    def __init__(self, text_widget):
        handler = TextHandler(text_widget)
        logging.basicConfig(
            level=logging.INFO,
            format='%(levelname)s - %(message)s',
            handlers=[handler]
        )
        self.logger = logging.getLogger(__name__)
        self.logger.info("Start of new logging session.")

    def get_logger(self):
        return self.logger
