from abc import ABCMeta, abstractmethod, abstractproperty

class Parser:
    __metaclass__ = ABCMeta

    @abstractmethod
    def __init__(self, log_path):
        """
        :param log_path: path of the log file
        """
        return

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