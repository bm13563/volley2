from logging import Formatter, StreamHandler, getLogger, DEBUG, INFO, WARNING, ERROR


class CustomFormatter(Formatter):
    """Logging Formatter to add colors and alter format"""

    level_suffix = "[%(asctime)s] %(levelname)s in %(filename)s:%(lineno)d: %(message)s"

    formats = {
        DEBUG: "\033[92m" + level_suffix,
        INFO: "\033[94m" + level_suffix,
        WARNING: "\033[93m" + level_suffix,
        ERROR: "\033[91m" + level_suffix,
    }

    def_keys = [
        "name",
        "msg",
        "args",
        "levelname",
        "levelno",
        "pathname",
        "filename",
        "module",
        "exc_info",
        "exc_text",
        "stack_info",
        "lineno",
        "funcName",
        "created",
        "msecs",
        "relativeCreated",
        "thread",
        "threadName",
        "processName",
        "process",
        "message",
    ]

    def format(self, record):
        log_fmt = self.formats.get(record.levelno)
        formatter = Formatter(log_fmt)
        extra = {k: v for k, v in record.__dict__.items() if k not in self.def_keys}
        if extra:
            extra_log = " - extra: " + str(extra)
        else:
            extra_log = ""
        return formatter.format(record) + extra_log + "\x1b[0m"


def get_logger(name="api", level=DEBUG):
    logger = getLogger(name)
    logger.setLevel(level)
    if not logger.handlers:
        log_handler = StreamHandler()
        log_handler.setFormatter(CustomFormatter())
        logger.addHandler(log_handler)
    return logger
