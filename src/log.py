import logging

class Log:
    def debug(self, msg):
        pass

    def info(self, msg):
        pass

    def warning(self, msg):
        pass

    def error(self, msg):
        pass


class LogLogging(Log):
    """
    logging framework와 호환되는 log 클래스
    """
    def __init__(self, logger):
        self.logger = logger

    def debug(self, msg):
        self.logger.debug(msg)

    def info(self, msg):
        self.logger.info(msg)

    def warning(self, msg):
        self.logger.warning(msg)

    def error(self, msg):
        self.logger.error(msg)


class LogQtlog(Log):
    """
    Qt framework와 호환되는 log 클래스
    """
    def __init__(self, logger):
        self.logger = logger

    def debug(self, msg):
        self.logger('DEBUG', msg)

    def info(self, msg):
        self.logger('INFO', msg)

    def warning(self, msg):
        self.logger('WARN', msg)

    def error(self, msg):
        self.logger('ERROR', msg)

CONSOLE = Log()

class QTextEditLogger(logging.Handler):
    def __init__(self,widget):
        super().__init__()
        self.widget = widget
        self.widget.setReadOnly(True)
        self.vertical_bar = widget.verticalScrollBar()

    def emit(self, record):
        msg = self.format(record)
        self.widget.append(msg)
        self.vertical_bar.setValue(self.vertical_bar.maximum())