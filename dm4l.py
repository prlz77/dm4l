import os
from importlib import import_module

import numpy as np

from logger import logger
from misc import LogStatus
from plotter import Plotter


class DM4L:
    def __init__(self):
        self.available_parsers = []
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'parsers')
        for d in os.listdir(path):
            dir = os.path.join(path, d)
            if os.path.isdir(dir):
                for f in os.listdir(dir):
                    file = os.path.join(dir, f)
                    if os.path.splitext(f)[1] == ".py" and "__init__" not in f:
                        self.available_parsers.append('%s.%s.%s' % ("parsers", d, f.replace('.py', '')))
        self.parsers = {}
        self.plotter = Plotter(self)
        self.log_list_file = None
        self.safe = False
        return

    def get_backends(self):
        return self.available_parsers

    def get_parsers(self):
        if self.safe:
            return self.get_safe_parsers()
        else:
            return self.parsers

    def update(self):
        for k in self.parsers:
            self.parsers[k].update()

    def add_log(self, log_path, backend_parser, id=None, pid=None):
        for k in self.parsers:
            if k == id:
                return None
        if backend_parser in self.available_parsers:
            parser_module = import_module(backend_parser)
            parser = parser_module.Parser(log_path)
            if id is None:
                id = log_path
            self.parsers[id] = parser
            logger.info('New log with id = %s was added.' %id)
        else:
            msg = "Backend %s not recognized\n" % (backend_parser)
            msg += "Please use one in %s (or call func get_backends()to list them)" % (str(self.available_parsers))
            raise ImportError(msg)

        return id

    def remove_log(self, id='', path='./'):
        keys = self.parsers.keys()
        for k in keys:
            if k == id or self.parsers[k].log_path == path:
                self.parsers[k].fp.close()
                self.parsers.pop(k, None)
                logger.info('logger with id = %s was removed' %k)

    def remove_all_logs(self):
        keys = self.parsers.keys()
        for k in keys:
            self.parsers[k].fp.close()

        self.parsers = {}

    def add_from_file(self, file_path=None):
        if file_path is not None:
            self.log_list_file = file_path
            if not os.path.exists(self.log_list_file):
                with open(self.log_list_file, 'a'):
                    pass

        if self.log_list_file is not None:
            with open(self.log_list_file, 'r') as infile:
                lfile = infile.readlines()
            for line in lfile:
                spline = line.replace('\n','').split(' ')
                if len(spline) >= 2:
                    id = None
                    pid = None
                    if len(spline) >= 3:
                        id=spline[2]
                    if len(spline) == 4:
                        pid=spline[3]

                    self.add_log(spline[0], spline[1], id, pid)

    def add_remove_from_file(self, file_path=None):
        if file_path is not None:
            self.log_list_file = file_path
            if not os.path.exists(self.log_list_file):
                with open(self.log_list_file, 'a'):
                    pass
        ids = []
        paths = []

        if self.log_list_file is not None:
            with open(self.log_list_file, 'r') as infile:
                lfile = infile.readlines()
            for line in lfile:
                spline = line.replace('\n','').split(' ')
                if len(spline) >= 2:
                    id = None
                    pid = None
                    if len(spline) >= 3:
                        id=spline[2]
                    else:
                        id = spline[0]
                    if len(spline) == 4:
                        pid=spline[3]
                    self.add_log(spline[0], spline[1], id, pid)
                    ids.append(id)
                    paths.append(spline[0])

        keys = self.parsers.keys()
        for k in keys:
            if k not in ids:
                self.remove_log(id=k)

    def get_max(self, parser_ids='all', value_field='test_acc'):
        if parser_ids == 'all':
            parser_ids = self.parsers.keys()
        assert (type(parser_ids) == list)
        max_list = np.zeros(len(parser_ids))
        arg_list = np.zeros(len(parser_ids))
        for i, parser_id in enumerate(parser_ids):
            y = self.parsers[parser_id].log_data[value_field]
            max_list[i] = np.max(y)
            arg_list[i] = np.argmax(y)

        max = np.max(max_list)
        id = parser_ids[np.argmax(max_list)]
        arg = arg_list[np.argmax(max_list)]
        return max, arg, id

    def get_safe_parsers(self):
        for id in self.parsers:
            if self.parsers[id].status != LogStatus.ERROR:
                self.safe_parsers[id] = self.parsers[id]

        return self.safe_parsers



