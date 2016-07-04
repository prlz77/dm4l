import os
import sys

from logger import logger

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from dm4l import DM4L
import argparse
from monitor import Monitor
from misc import Commands
import logging

def plot(dm4l, x, y, title, legend, plot_params):
    dm4l.plotter.multi_plot(x, y, 'all', title, legend, plot_params)

if __name__ == '__main__':
    dm4l = DM4L()
    parser = argparse.ArgumentParser(description='~ Dark Magic 4 Logs ~')
    parser.add_argument('--logs', type=str, default=None, nargs='+', help="[list] of log file[s]. Overrides file reading")
    parser.add_argument('--backends', type=str, default=None, nargs='+', choices=dm4l.get_backends(),
                        help="The respective backend for each log[s]")
    parser.add_argument('--from_file', type=str, default='./parsers.conf', help="Reads: log_path<space>backend\\nlog_path... from here")
    parser.add_argument('--safe', action='store_false', help="Ignore erroneous logs")
    parser.add_argument('--silent', action='store_true', help='Do not show warnings')
    parser.add_argument('--refresh', type=int, default=0, help="Seconds to refresh data. 0 = run once.")
    subparsers = parser.add_subparsers(dest='subcommand')
    parser_max = subparsers.add_parser('max')
    parser_max.add_argument('--format', default=[0], type=int, nargs='+',
                        help="any combination of 0,1,2 where 0 = max, 1 = argmax, 2 = maxid. Ex: 0 2 = max_value id")
    parser_plot = subparsers.add_parser('plot')
    parser_plot.add_argument('-x', type=str, default='epoch')
    parser_plot.add_argument('-y', type=str, nargs='+', default=['test_acc'])
    parser_plot.add_argument('--title', type=str, default='')
    parser_plot.add_argument('--no_legend', action='store_false')
    parser_plot.add_argument('--format', type=dict, default={}, help="Dictionary format")
    parser_report = subparsers.add_parser('report')

    args = parser.parse_args()

    if args.silent:
        logger.setLevel(logging.FATAL)
    else:
        logger.setLevel(logging.INFO)

    dm4l = DM4L()
    if args.logs is not None and args.backends is not None:
        if len(args.logs > 0):
            if len(args.backends) == 1 and len(args.logs > 1):
                args.backends *= len(args.logs)
        assert(len(args.backends) == len(args.logs))
        for l,b in zip(args.logs, args.backends):
            dm4l.add_log(l,b)
    else:
        dm4l.add_from_file(args.from_file)

    monitor = Monitor(dm4l, safe=args.safe)
    if args.subcommand == 'max':
        monitor.set_command(Commands.MAX, {'format':args.format})
    elif args.subcommand == 'plot':
        monitor.set_command(Commands.PLOT, {'x':args.x, 'y':args.y, 'title':args.title, 'legend':args.no_legend, 'format':args.format})


    if args.refresh > 0:
        monitor.refresh = args.refresh
        monitor.run()
    else:
        monitor.run_once()


