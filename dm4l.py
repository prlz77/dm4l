import glob
import os
from importlib import import_module

import numpy as np

from graphics.plotter import Plotter
from logger import logger
from misc import LogStatus


class DM4L:
    FROM_FILE = 1
    FROM_FOLDER = 2
    FROM_LIST = 3

    def __init__(self):
        self.available_handlers = []
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'handlers')
        for d in os.listdir(path):
            dir = os.path.join(path, d)
            if os.path.isdir(dir):
                for d2 in os.listdir(dir):
                    dir2 = os.path.join(dir, d2)
                    if os.path.isdir(dir2):
                        if os.path.isfile(os.path.join(dir2,'handler.py')):
                            if not os.path.isfile(os.path.join(dir2, '__init__.py')):
                                with os.path.join(dir2, '__init__.py', 'w') as outfile:
                                    outfile.write('from handler import LogHandler')
                            self.available_handlers.append('%s.%s' % (d, d2))

        self.log_handlers = {}
        self.plotter = Plotter(self)
        self.input = None
        self.input_mode = None
        self.safe = False
        return

    def set_safe(self, value):
        self.safe = value

    def set_input(self, mode, input):
        self.remove_all_logs()
        if mode in [DM4L.FROM_FILE, DM4L.FROM_FOLDER]:
            self.input_mode = mode
        elif mode == DM4L.FROM_LIST:
            self.input_mode = mode
        self.input = input

    def update_input(self):
        if self.input_mode == DM4L.FROM_FILE:
            self.add_from_file()
        elif self.input_mode == DM4L.FROM_FOLDER:
            self.add_from_folder(self.input[0], self.input[1])

    def get_backends(self):
        return self.available_handlers

    def get_handlers(self):
        if self.safe:
            return self.get_safe_handlers()
        else:
            return self.log_handlers

    def update(self):
        result = False
        for k in self.log_handlers:
            result = self.log_handlers[k].update() or result
        return result

    def add_log(self, log_path, backend_handler, id=None, pid=None):
        for k in self.log_handlers:
            if id is not None and k == id or id is None and log_path == k:
                return k
        if backend_handler in self.available_handlers:
            handler_module = import_module('handlers.' + str(backend_handler))
            handler = handler_module.LogHandler(log_path)
            if id is None:
                id = log_path
            self.log_handlers[id] = handler
            self.log_handlers[id].set_pid(pid)
            logger.info('New log with id = %s was added.' %id)
        else:
            msg = "Backend %s not recognized\n" % (backend_handler)
            msg += "Please use one in %s (or call func get_backends()to list them)" % (str(self.available_handlers))
            raise ImportError(msg)

        return id

    def remove_log(self, id='', path='./'):
        keys = self.log_handlers.keys()
        for k in keys:
            if k == id or self.log_handlers[k].log_path == path:
                self.log_handlers[k].fp.close()
                self.log_handlers.pop(k, None)
                logger.info('logger with id = %s was removed' %k)

    def remove_all_logs(self):
        keys = self.log_handlers.keys()
        for k in keys:
            self.log_handlers[k].fp.close()

        self.log_handlers = {}

    def add_from_folder(self, pattern, backend):
        ids = []
        for file in glob.glob(pattern):
            if os.path.isfile(file):
                id = self.add_log(file,backend)
                ids.append(id)
        keys = self.log_handlers.keys()
        for k in keys:
            if k not in ids:
                self.remove_log(id=k)

    def add_from_file(self, file_path=None):
        if file_path is not None:
            self.input = file_path
            if not os.path.exists(self.input):
                with open(self.input, 'a'):
                    pass
        ids = []
        paths = []

        if self.input is not None:
            with open(self.input, 'r') as infile:
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

        keys = self.log_handlers.keys()
        for k in keys:
            if k not in ids:
                self.remove_log(id=k)

    def get_max(self, handler_ids='all', value_field='test_acc'):
        if handler_ids == 'all':
            handler_ids = self.log_handlers.keys()
        assert (type(handler_ids) == list)
        max_list = np.zeros(len(handler_ids))
        arg_list = np.zeros(len(handler_ids))
        for i, handler_id in enumerate(handler_ids):
            y = self.log_handlers[handler_id].log_data[value_field]
            max_list[i] = np.max(y)
            arg_list[i] = np.argmax(y)

        max = np.max(max_list)
        id = handler_ids[np.argmax(max_list)]
        arg = arg_list[np.argmax(max_list)]
        return max, arg, id

    def get_safe_handlers(self):
        safe_handlers = {}
        for id in self.log_handlers:
            if self.log_handlers[id].status != LogStatus.ERROR:
                safe_handlers[id] = self.log_handlers[id]

        return safe_handlers



