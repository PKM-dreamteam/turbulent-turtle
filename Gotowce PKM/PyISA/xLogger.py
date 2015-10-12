__author__ = 'mikhael'

import logging
import sys
from PyQt4.QtCore import QObject, pyqtSignal

alertHtml = "<font color=\"Red\">"
warningHtml = "<font color=\"Green\">"
infoHtml = "<font color=\"Blue\">"
endHtml = "</font> <br />"


class XStream(QObject, object):
    """
    XStream class of logging to multiple elements
    """
    _stdout = None
    _stderr = None
    messageWritten = pyqtSignal(unicode)

    @staticmethod
    def flush():
        """
        Flush method
        """
        pass

    @staticmethod
    def fileno():
        """
        File no method
        """
        return -1

    def write(self, msg):
        """
        Writing massage to multiple elements
        :param msg:
        """
        if not self.signalsBlocked():
            self.messageWritten.emit(unicode(msg))

    @staticmethod
    def stdout():
        """
        Standard out method
        :return:
        """
        if not XStream._stdout:
            XStream._stdout = XStream()
            sys.stdout = XStream._stdout
        return XStream._stdout

    @staticmethod
    def stderr():
        """
        Standard error method
        :return:
        """
        if not XStream._stderr:
            XStream._stderr = XStream()
            sys.stderr = XStream._stderr
        return XStream._stderr


class XLogger(object):
    """
    XLogger class
    """
    def __init__(self, name):
        self.logger = logging.getLogger(name)
        self.type = True

    # def debug(self, text):
    #     """
    #     Debug info
    #     :param text: text
    #     """
    #     print text + '\n'
    #     self.logger.debug(text)

    def info(self, text):
        """
        Standard info
        :param text: text
        """
        if self.type:
            print unicode(text)
        else:
            print infoHtml + unicode(text) + endHtml
            self.logger.info(text)

    def warning(self, text):
        """
        Warning info
        :param text: text
        """
        if self.type:
            print unicode(text)
        else:
            print warningHtml + unicode(text) + endHtml
            self.logger.warning(text)

    def error(self, text):
        """
        Error info
        :param text: text
        """
        if self.type:
            print unicode(text)
        else:
            print alertHtml + unicode(text) + endHtml
            self.logger.error(text)