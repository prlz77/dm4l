import logging
from abc import ABCMeta, abstractmethod

from misc import LogStatus

parser_settings = {}

class AbstractParser:
    __metaclass__ = ABCMeta

    def __init__(self, log_path):
        """
        :param log_path: path of the log file
        :param id: Id for further reference to concrete parsers
        """
        self.fp = open(log_path, 'r')
        self.log_data = {}
        self.log_path = log_path
        self.status = LogStatus.INIT # INIT, TRAINING, ERROR, FINISHED
        self.parser_settings = {}
    @abstractmethod
    def get_data(self):
        """
        :return: dictionary of lists for each field in log. Detected fields are:
                    train_acc in (%)
                    test_acc in (%)
                    epoch (1 to inf)
                    lr (1 value per epoch)
                    custom fields
        """
        return

    @abstractmethod
    def _update(self):
        """
        Appends file updates to the log
        """

    def update(self):
        """
        Makes the update step safe. There is no need to override.
        """
        if self.status != LogStatus.ERROR or \
          (self.status == LogStatus.FINISHED and self.log_data == {}) or \
           self.status == LogStatus.TRAINING:
            try:
                self._update()
            except:
                self.status = LogStatus.ERROR
                logging.getLogger('dm4l').warn("Error parsing %s" %self.log_path)