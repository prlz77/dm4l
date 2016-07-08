# -*- coding: utf-8 -*-
# Author: prlz77 <pau.rodriguez at gmail.com>
# Group: ISELAB@CVC-UAB
# Date: 05/07/2016
"""
Dark magic commandline interface.

How to use it
=============
1. Run-once mode, like any other shell command. For instance:
``python main.py --silent --path ./logs/*.log backend max --format 2 0 1``
The ``--silent`` option is needed so that only the output is printed. Then we can use pipes, for instance.
This will output three values:  path_of_the_log_with_max_accuracy max_accuracy argmax_accuracy

2. Monitor mode, to report in "real" time.
``python main.py --refresh 1 --path ./logs/*.log backend plot``
This will read all the logs matching the pattern and plot them in real time. It will refresh
every 1 seconds.
"""

import argparse
import logging
import os
import sys

from logger import logger

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from dm4l import DM4L

if __name__ == '__main__':
    dm4l = DM4L()
    parser = argparse.ArgumentParser(description='~ Dark Magic 4 Logs ~')
    # Global arguments
    group = parser.add_mutually_exclusive_group(required=False)
    group.add_argument('--logs', type=str, nargs=2, help="""log_path1,log_path2 backend1[,backend2...]
    The backend should be in %s""" %str(dm4l.get_available_handlers()))
    group.add_argument('--file', type=str, default='./monitors.conf', help="Reads: log_path<space>backend\\nlog_path... from here")
    group.add_argument('--path', type=str, default=None, nargs=2, help="Reads all logs in path. Ex. --path ./*.log")
    parser.add_argument('--safe', action='store_false', help="Ignore erroneous logs")
    parser.add_argument('--silent', action='store_true', help='Do not show warnings')
    parser.add_argument('--refresh', type=int, default=0, help="Seconds to refresh data. 0 = run once.")
    parser.add_argument('plug', type=str, nargs='+', help="list plugins to activate")

    args = parser.parse_args()

    if args.silent:
        logger.setLevel(logging.FATAL)
    else:
        logger.setLevel(logging.INFO)
        with open(os.path.join(os.path.dirname(__file__), 'logo.txt'),'r') as infile:
            logger.info(infile.read())
            [h.flush() for h in logger.handlers]

    dm4l = DM4L()
    dm4l.set_safe(True)
    if args.logs is not None:
        args.logs[0] = args.logs[0].split(',')
        args.logs[1] = args.logs[1].split(',')
        if len(args.logs[1]) == 1 and len(args.logs[1]) < len(args.logs[0]):
            args.logs[1] *= len(args.logs[0])
        assert(len(args.logs[1]) == len(args.logs[0]))
        dm4l.set_input(DM4L.FROM_LIST, args.logs)
    elif args.path is not None:
        dm4l.set_input(DM4L.FROM_FOLDER, args.path)
    elif args.file is not None:
        dm4l.set_input(DM4L.FROM_FILE, args.file)

    for plug in args.plug:
        dm4l.set_active_plugin(plug, True)

    dm4l.refresh = args.refresh
    dm4l.run()

