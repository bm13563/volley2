import logging

class CustomFormatter(logging.Formatter):
    """Logging Formatter to add colors and alter format"""
    level_suffix = "[%(asctime)s] %(levelname)s in %(filename)s:%(lineno)d: %(message)s" + "\x1b[0m"

    FORMATS = {
        logging.DEBUG: "\033[92m" + level_suffix,
        logging.INFO: "\033[94m" + level_suffix,
        logging.WARNING: "\033[93m" + level_suffix,
        logging.ERROR: "\033[91m" + level_suffix,
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)