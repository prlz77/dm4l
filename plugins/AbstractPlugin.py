import logging
from abc import ABCMeta, abstractmethod


class AbstractPlugin(object):
    __metaclass__ = ABCMeta

    def __init__(self, dm4l, config):
        self.dm4l = dm4l
        self.config = config

    def set_config(self, key, value):
        if key in self.config:
            assert(isinstance(value, type(self.config[key])))  # Can avoid user errors.
            self.config[key] = value
        else:
            logging.getLogger('dm4l').warn('unrecognized key')

    @abstractmethod
    def update(self, ids=[]):
        return NotImplementedError