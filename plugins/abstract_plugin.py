import logging
from abc import ABCMeta, abstractmethod


class AbstractPlugin(object):
    """
    Abstract Plugin class. It receives the powers of dark magic and a configuration dictionary. Users should override
    the update method for the desired functionality.
    """
    __metaclass__ = ABCMeta

    def __init__(self, dm4l, config):
        self.dm4l = dm4l
        self.config = config

    def set_config(self, key, value):
        """ Change a configuration parameter.

        :param key: ``string`` name of the parameter.
        :param value: value to change.
        :return:
        """
        if key in self.config:
            assert(isinstance(value, type(self.config[key])))  # Can avoid user errors.
            self.config[key] = value
        else:
            logging.getLogger('dm4l').warn('unrecognized key')

    @abstractmethod
    def update(self, ids=[]):
        """ Should be implemented by the user. Performs the main function.

        :param ids: ``list`` of ids of the target log handlers.
        :return:
        """
        return NotImplementedError