import logging
from abc import ABCMeta, abstractmethod
from misc import LogStatus
import psutil


class AbstractLogHandler:
    __metaclass__ = ABCMeta

    def __init__(self, log_path):
        """
        :param log_path: path of the log file
        :param id: Id for further reference to concrete handlers
        """
        self.fp = open(log_path, 'r')
        self.log_data = {}
        self.persistent_log_data = {}
        self.log_path = log_path
        self.status = LogStatus.INIT # INIT, TRAINING, ERROR, FINISHED
        self.handler_settings = {}
        self.past_data = {}
        self.change_flag = False
        self.pid = None

    def set_pid(self, pid):
        self.pid = pid

    def has_changed(self):
        return self.change_flag

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
    def parse(self):
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
                self.change_flag = self.parse()
                assert(type(self.change_flag) == bool)
                assert('test_acc' in self.log_data)
                assert('epoch' in self.log_data)
            except AssertionError as e:
                if 'test_acc' not in self.log_data:
                    e.args += ("test_acc field not found.",)
                if 'epoch' not in self.log_data:
                    e.args += ("epoch field not found.",)
                if type(self.change_flag) != bool:
                    e.args += (" _update should return True if file changed and False otherwise",)
                logging.getLogger('dm4l').error("Error parsing %s" %self.log_path)
                raise e
            except:
                self.status = LogStatus.ERROR
                logging.getLogger('dm4l').warn("Error parsing %s." %self.log_path)

            if self.pid is not None:
                if not psutil.pid_exists(self.pid):
                    self.status = LogStatus.FINISHED
        return self.change_flag