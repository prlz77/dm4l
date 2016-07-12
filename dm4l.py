# -*- coding: utf-8 -*-
# Author: prlz77 <pau.rodriguez at gmail.com>
# Group: ISELAB@CVC-UAB
# Date: 05/07/2016
"""Dark Magic For Logs (DM4L)

Uses dark magic to deal with epoch/score logs in any format. It allows:

- **Comparing** different logs. For example getting the max accuracy between model1 trained in torch and model2 trained
  in caffe. Or even **plotting** them.
- **Monitoring** logs. See if your models are training correctly, program early stopping, etc.
- Information **reports**. Create a report with your training log data and serve it like in NVIDIA DIGITS.

"""

import glob
import os
import logging
import time
import sys
import numpy as np
from importlib import import_module
from logger import logger
from handlers.abstract_log_handler import HandlerStatus


class DM4L:
    """
    The main module of the project.
    Handles multiple logs and extracts information from them.
    """

    FROM_FILE = 1
    """ Input from file flag """
    FROM_FOLDER = 2
    """ Input from folder flag """
    FROM_LIST = 3
    """ Input from  list flag """

    def __init__(self):
        self.dark_path = os.path.dirname(os.path.abspath(__file__))
        self.refresh = 0
        self.log_handlers = {}
        self.input = None
        self.input_mode = None
        self.safe = False
        self.plugins = {}
        self.get_available_handlers()
        self.active_plugins = []
        self.end = False

    def get_plugins(self):
        """

        :return: a dictionary with the loaded plugins.
        """
        return self.plugins

    def get_active_plugins(self):
        """

        :return: a list with the names of the currently active plugins
        """
        return self.active_plugins

    def load_plugin(self, name, active, extra_config={}):
        """ Loads (and activates) a plugin

        :param name: ``string`` name of the plugin
        :param active: ``bool`` True to activate and False to deacivate
        :param extra_config: list of configuration key/values to override
        :return:
        """

        if name not in self.plugins:
            path = os.path.join(self.dark_path,'plugins', name)
            if os.path.isdir(path):
                if 'plugin.py' in os.listdir(path):
                    plugin = import_module("%s.%s.%s" % ('plugins', name, 'plugin'))
                    if 'config.py' in os.listdir(path):
                        config = import_module("%s.%s.%s" % ('plugins', name, 'config')).config
                    else:
                        config = {}
                    self.plugins[name] = plugin.Plugin(self, config)
        for k in extra_config:
            self.plugins[name].set_config(k, extra_config[k])

        if active:
            if name not in self.active_plugins:
                self.active_plugins.append(name)
                logging.getLogger('dm4l').info("Activated %s" %name)
            else:
                logging.getLogger('dm4l').warn("Trying to activate %s, an already active plugin." %name)
        else:
            if name in self.active_plugins:
                self.active_plugins.remove(name)
                logging.getLogger('dm4l').info("Deactivated %s" % name)

    def get_available_handlers(self):
        """ Get the supported log handlers.

        :return: A string list with all the supported log handlers.
        """
        self.available_handlers = []
        path = os.path.join(self.dark_path, 'handlers')
        for d in os.listdir(path):
            dir = os.path.join(path, d)
            if os.path.isdir(dir):
                for d2 in os.listdir(dir):
                    dir2 = os.path.join(dir, d2)
                    if os.path.isdir(dir2):
                        if os.path.isfile(os.path.join(dir2,'handler.py')):
                            if not os.path.isfile(os.path.join(dir2, '__init__.py')):
                                with os.path.join(dir2, '__init__.py', 'a') as outfile:
                                    pass
                            self.available_handlers.append('%s.%s' % (d, d2))
        return self.available_handlers

    def get_handlers(self):
        """ Get the active log handlers.

        :return: A dictionary with all the active log handlers.
        """
        if self.safe:
            return self.get_safe_handlers()
        else:
            return self.log_handlers

    def get_safe_handlers(self):
        """ Get the non erroneous handlers.

        :return: Returns a list with the non erroneous handlers.
        """
        safe_handlers = {}
        for id in self.log_handlers:
            if self.log_handlers[id].status != HandlerStatus.ERROR:
                safe_handlers[id] = self.log_handlers[id]

        return safe_handlers

    def set_safe(self, value):
        """
        Sets ``self.safe``. When safe, handlers reporting errors are ignored.

        :param value: ``bool``
        """
        self.safe = value

    def set_input(self, mode, input):
        """Tells DM4L where to look for the log files.

        :param mode: Choose from ``{DM4L.FROM_FILE, DM4L.FROM_FOLDER, DM4L.FROM_LIST}``
        :param input: If mode is
                        - DM4L.FROM_FILE: path ``string`` to a file with ``log_path<space>backend<space>[id<space>pid<space>]``\n
                        - DM4L.FROM_FOLDER: path ``string`` to the logs. E.g. './*.txt'
                        - DM4L.FROM_LIST: ``[string list, string list]`` like  ``[[log1,log2,etc],[backend1,backend2,etc]]``

        """
        self.remove_all_logs()
        if mode in [DM4L.FROM_FILE, DM4L.FROM_FOLDER]:
            self.input_mode = mode
        elif mode == DM4L.FROM_LIST:
            self.input_mode = mode
            for log, backend in zip(input[0], input[1]):
                self.add_log(log, backend)
        self.input = input

    def update_input(self):
        """ Updates the list of handled logs.

        :return:
        """
        if self.input_mode == DM4L.FROM_FILE:
            self.add_from_file()
        elif self.input_mode == DM4L.FROM_FOLDER:
            self.add_from_folder(self.input[0], self.input[1])

    def update(self):
        """ Updates the state of all the log handlers.

        :return: True if any change, False if no changes.
        """
        result = False
        for k in self.log_handlers:
            result = self.log_handlers[k].update() or result
        return result

    def add_log(self, log_path, backend_handler, id=None, pid=None):
        """ Handle a new log.

        :param log_path: path of the log file.
        :param backend_handler:  kind of handle to use.
        :param id: to provide a custom id. Default is log_path
        :param pid: optional. The training process identifier.
        :return: assigned id
        """
        for k in self.log_handlers:
            if id is not None and k == id or id is None and log_path == k:
                return k
        if backend_handler in self.available_handlers:
            handler_module = import_module('handlers.' + str(backend_handler) + '.handler')
            handler = handler_module.LogHandler(log_path)
            if id is None:
                id = log_path
            self.log_handlers[id] = handler
            self.log_handlers[id].set_pid(pid)
            logger.info('New log with id = %s was added.' %id)
        else:
            msg = "Backend %s not recognized\n" % (backend_handler)
            msg += "Please use one in %s (or call func get_available_handlers()to list them)" % (str(self.available_handlers))
            raise ImportError(msg)

        return id

    def add_from_folder(self, pattern, backend):
        """ Handle all logs from a given input pattern.

        :param pattern: path. For instance: ./*.log
        :param backend: backend handler for all the logs in this path.
        :return:
        """
        ids = []
        for file in glob.glob(pattern):
            if os.path.isfile(file):
                id = self.add_log(file, backend)
                ids.append(id)
        keys = self.log_handlers.keys()
        for k in keys:
            if k not in ids:
                self.remove_log(id=k)

    def add_from_file(self, file_path=None):
        """ Handle all logs from an input file.

        :param file_path: file containing log_path backend [id] [pid]\n. If None, it updates from the last file_path.
        :return:
        """
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

    def remove_log(self, id='', path='./'):
        """ Remove a handled log by its id or path

        :param id: id to remove
        :param path: path to remove
        :return:
        """
        keys = self.log_handlers.keys()
        for k in keys:
            if k == id or self.log_handlers[k].log_path == path:
                self.log_handlers[k].fp.close()
                self.log_handlers.pop(k, None)
                logger.info('logger with id = %s was removed' %k)

    def remove_all_logs(self):
        """ Remove all handled logs.

        :return:
        """
        keys = self.log_handlers.keys()
        for k in keys:
            self.log_handlers[k].fp.close()

        self.log_handlers = {}

    def run(self):
        """ Main loop

        :return:
        """
        if self.refresh > 0:
            logging.getLogger('dm4l').info('Running...')
            try:
                while not self.end:
                    self.update_input()
                    self.update()
                    for plugin in self.active_plugins:
                        self.plugins[plugin].update()
                    time.sleep(self.refresh)
            except KeyboardInterrupt:
                logging.getLogger('dm4l').warn('\nExiting by user request.\n')
                sys.exit(0)
        else:
            self.update_input()
            self.update()
            for plugin in self.active_plugins:
                self.plugins[plugin].update()
            time.sleep(self.refresh)