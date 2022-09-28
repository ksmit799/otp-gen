import coloredlogs
import logging


class LoggingNotifier:
    notifyLevel = "WARNING"

    def __init__(self, category):
        # create a new Python logging object in which will actually
        # log the messages to stdout...
        self.__logger = logging.getLogger(category)

        # set up the colored logging module for this new logger
        # object, so we can have colored logs...
        coloredlogs.install(
            level=LoggingNotifier.notifyLevel,
            logger=self.__logger,
        )

    def info(self, message):
        self.__logger.info(message)
        return True

    def debug(self, message):
        self.__logger.debug(message)
        return True

    def warning(self, message):
        self.__logger.warning(message)

    def error(self, message):
        self.__logger.error(message)


class LoggingNotify:
    def __init__(self):
        self.__categories = {}

    def new_category(self, category):
        notifier = self.__categories.get(category)
        if not notifier:
            notifier = LoggingNotifier(category)
            self.__categories[category] = notifier

        return notifier


notify = LoggingNotify()
