import numpy as np
from misc import LogStatus
import matplotlib
matplotlib.use('TkAgg')
try:
    import seaborn as sns
except ImportError:
    print 'Install seaborn for nice looking plots.'

import pylab

class Plotter:
    def __init__(self, parsers):
        self.plot_params = {'y_min': 0, 'y_max': 100, 'scale': 100, 'score': 'acc'}
        self.parsers = parsers
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

    def plot(self, x_field, y_field, monitor_id, title=None, legend=False, plot_params={}):
        if self.parsers[monitor_id].status != LogStatus.ERROR:
            for k in self.plot_params:
                if k not in plot_params:
                    plot_params[k] = self.plot_params[k]
            if title is None:
                title = monitor_id
            data = self.parsers[monitor_id].get_data()
            x = data[x_field]
            y = self.process_y(data[y_field][:])
            ax = pylab.plot(x, y)
            pylab.title(title)
            pylab.xlabel(x_field)
            pylab.ylabel(y_field)
            pylab.ylim(plot_params['y_min'], plot_params['y_max'])
            if legend:
                ax.legend([y_field])
            pylab.show()
        else:
            return False
        return True

    def multi_plot(self, x_field, y_fields, monitor_ids='all', title=None, legend=False, plot_params={}):
        assert (type(y_fields) == list)
        assert (type(monitor_ids) == list)
        for k in self.plot_params:
            if k not in plot_params:
                plot_params[k] = self.plot_params[k]
        if monitor_ids == 'all':
            ids = self.parsers.keys()
        else:
            ids = monitor_ids
        pylab.figure()
        pylab.hold(True)
        l_legend = []
        for monitor_id in ids:
            if self.parsers[monitor_id].status != LogStatus.ERROR:
                data = self.parsers[monitor_id].get_data()
                x = np.array(data[x_field])
                for y_field in y_fields:
                    y = self.process_y(np.array(data[y_field]))
                    pylab.plot(x, y)
                    pylab.xlabel(x_field)
                    if len(set(y_fields)) == 1:
                        l_legend += [monitor_id]
                    else:
                        l_legend += [y_field + ' ' + monitor_id]
            else:
                return False
        if len(set(y_fields)) == 1:
            pylab.ylabel(y_field)
        if title is not None:
            pylab.title(title)
        pylab.ylim(plot_params['y_min'], plot_params['y_max'])
        if legend:
            pylab.legend(l_legend)
        pylab.show()
        return True