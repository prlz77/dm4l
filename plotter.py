import logging
import matplotlib
import numpy as np
from misc import LogStatus

matplotlib.use('TkAgg')
try:
    import seaborn as sns
except ImportError:
    logging.getLogger('dm4l').info('Install seaborn for nice looking plots.')

import pylab
pylab.ion()

class Plotter:
    def __init__(self, dm4l):
        self.plot_params = {'y_min': 0, 'y_max': 100, 'scale': 100, 'score': 'acc'}
        self.dm4l = dm4l

    def set_plot_param(self, key, value):
        if key == 'y_min':
            pass
        elif key == 'y_max':
            pass
        elif key == 'score':
            assert (value in ['err', 'acc'])
        elif key == 'scale':
            assert (value > 0)
            self.set_plot_param('y_max', value)

        self.plot_params[key] = value

    def set_plot_params(self, plot_params={}):
        for k in plot_params:
            self.set_plot_param(k, plot_params[k])

    def process_y(self, y):
        y2 = y.copy()
        max_value = 100. / self.plot_params['scale']
        y2 /= max_value
        if self.plot_params['score'] == 'err':
            y2 = self.plot_params['scale'] - y2

        return y2

    def plot(self, x_field, y_field, parser_id, title=None, legend=False, plot_params={}):
        assert(type(y_field) == str)
        if len(self.dm4l.get_parsers().keys()) == 0:
            return True

        if self.dm4l.get_parsers()[parser_id].status != LogStatus.ERROR:
            for k in self.plot_params:
                if k not in plot_params:
                    plot_params[k] = self.plot_params[k]
            if title is None:
                title = parser_id
            data = self.dm4l.get_parsers()[parser_id].get_data()
            x = data[x_field]
            y = self.process_y(np.array(data[y_field][:]))
            ax = pylab.plot(x, y)
            pylab.title(title)
            pylab.xlabel(x_field)
            pylab.ylabel(y_field)
            pylab.ylim(plot_params['y_min'], plot_params['y_max'])
            if legend:
                pylab.legend([y_field])
            pylab.show()
        else:
            return False
        return True

    def multi_plot(self, x_field, y_fields, parser_ids='all', title=None, legend=False, plot_params={}):
        if len(self.dm4l.get_parsers().keys()) == 0:
            return True
        if parser_ids == 'all':
            ids = self.dm4l.get_parsers().keys()
        else:
            ids = parser_ids
        assert (type(y_fields) == list)
        assert (type(ids) == list)
        for k in self.plot_params:
            if k not in plot_params:
                plot_params[k] = self.plot_params[k]
        #pylab.figure()
        pylab.hold(True)
        pylab.cla()
        l_legend = []
        for parser_id in ids:
            if self.dm4l.get_parsers()[parser_id].status != LogStatus.ERROR:
                data = self.dm4l.get_parsers()[parser_id].get_data()
                x = np.array(data[x_field])
                for y_field in y_fields:
                    y = self.process_y(np.array(data[y_field]))
                    pylab.plot(x, y)
                    pylab.xlabel(x_field)
                    if len(set(y_fields)) == 1:
                        l_legend += [parser_id]
                    else:
                        l_legend += [y_field + ' ' + parser_id]
            else:
                return False
        if len(set(y_fields)) == 1:
            pylab.ylabel(y_field)
        if title is not None:
            pylab.title(title)
        pylab.ylim(plot_params['y_min'], plot_params['y_max'])
        if legend:
            pylab.legend(l_legend)

        pylab.draw()
        pylab.pause(0.0001)
        return True