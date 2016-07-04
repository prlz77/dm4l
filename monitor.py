import sys
import time

from misc import Commands


class Monitor():
    def __init__(self, dm4l_instance, command={}, options={}, safe=True, refresh=1):
        self.dm4l = dm4l_instance
        self.refresh = refresh
        self.end = False
        self.command = command
        self.options = options

    def set_command(self, command, options):
        self.command = command
        self.options = options

    def print_max(self):
        max = self.dm4l.get_max()
        res = []
        for i in self.options['format']:
            res.append(str(max[i]))
        print ' '.join(res)

    def plot(self):
        if 'title' not in self.options:
            self.options['title'] = ''
        if 'legend' not in self.options:
            self.options['legend'] = False
        if 'format' not in self.options:
            self.options['format'] = {}
        self.dm4l.plotter.multi_plot(self.options['x'], self.options['y'],
                                     'all', self.options['title'], self.options['legend'], self.options['format'])

    def update(self):
        self.dm4l.add_remove_from_file()
        self.dm4l.update()
        if self.command == Commands.MAX:
            self.print_max()
        elif self.command == Commands.PLOT:
            self.plot()

    def run(self):
        print 'Running monitor...'
        try:
            while not self.end:
                self.update()
                time.sleep(1)
        except KeyboardInterrupt:
            print >> sys.stderr, '\nExiting by user request.\n'
            sys.exit(0)

    def run_once(self):
        self.update()