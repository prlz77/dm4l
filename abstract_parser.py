from abc import ABCMeta, abstractmethod, abstractproperty
from misc import LogStatus

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
    def update(self):
        """
        Appends file updates to the log
        """