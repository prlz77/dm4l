from importlib import import_module
from misc import LogStatus
import numpy as np
from plotter import Plotter
import os

class DM4L:
    def __init__(self):
        self.available_parsers = []
        for d in os.listdir('parsers'):
            dir = os.path.join('parsers', d)
            if os.path.isdir(dir):
                for f in os.listdir(dir):
                    file = os.path.join(dir, f)
                    if ".py" in f and "__init__" not in f:
                        self.available_parsers.append('%s.%s.%s' %("parsers", d, f.replace('.py','')))
        self.parsers = {}
        self.plotter = Plotter(self.parsers)
        return

    def get_parsers(self):
        return self.available_parsers

    def update(self):
        for k in self.parsers:
            self.parsers[k].update()

    def add_log(self, log_path, backend_parser, id=None, pid=None):
        if backend_parser in self.available_parsers:
            parser_module = import_module(backend_parser)
            parser = parser_module.Parser(log_path)
            if id is None:
                id = log_path
            self.parsers[id] = parser
        else:
            msg = "Backend %s not recognized\n" %(backend_parser)
            msg += "Please use one in %s (or call func get_parsers()to list them)" %(str(self.available_parsers))
            raise ImportError(msg)

        return id

