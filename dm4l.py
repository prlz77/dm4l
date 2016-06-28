from importlib import import_module
from misc import LogStatus
import numpy as np
import matplotlib
matplotlib.use('TkAgg')
try:
    import seaborn as sns
except ImportError:
    print 'Install seaborn for nice looking plots.'

import pylab
import os

class DM4L:
    def __init__(self):
        self.parsers = []
        for d in os.listdir('parsers'):
            dir = os.path.join('parsers', d)
            if os.path.isdir(dir):
                for f in os.listdir(dir):
                    file = os.path.join(dir, f)
                    if ".py" in f and "__init__" not in f:
                        self.parsers.append('%s.%s.%s' %("parsers", d, f.replace('.py','')))
        self.monitors = {}
        self.plot_params = {'y_min':0, 'y_max':100, 'scale':100, 'score': 'acc'}
        return

    def get_parsers(self):
        return self.parsers

    def update(self):
        for k in self.monitors:
            self.monitors[k].update()

    def add_log(self, log_path, backend_parser, id=None):
        if backend_parser in self.parsers:
            parser_module = import_module(backend_parser)
            parser = parser_module.Parser(log_path)
            if id is None:
                id = log_path
            self.monitors[id] = parser
        else:
            msg = "Backend %s not recognized\n" %(backend_parser)
            msg += "Please use one in %s (or call func get_parsers()to list them)" %(str(self.parsers))
            raise ImportError(msg)

        return id

    def set_plot_param(self, key, value):
        if key == 'y_min':
            pass
        elif key == 'y_max':
            pass
        elif key == 'score':
            assert(value in ['err', 'acc'])
        elif key == 'scale':
            assert(value > 0)
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
        if self.monitors[monitor_id].status != LogStatus.ERROR:
            for k in self.plot_params:
                if k not in plot_params:
                    plot_params[k] = self.plot_params[k]
            if title is None:
                title = monitor_id
            data = self.monitors[monitor_id].get_data()
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
        assert(type(y_fields) == list)
        assert(type(monitor_ids) == list)
        for k in self.plot_params:
            if k not in plot_params:
                plot_params[k] = self.plot_params[k]
        if monitor_ids == 'all':
            ids = self.monitors.keys()
        else:
            ids = monitor_ids
        pylab.figure()
        pylab.hold(True)
        l_legend = []
        for monitor_id in ids:
            if self.monitors[monitor_id].status != LogStatus.ERROR:
                data = self.monitors[monitor_id].get_data()
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


m = DM4L()
m.set_plot_param('score', 'err')
m.set_plot_param('scale', 1)
id = m.add_log('/home/prlz77/Code/wide-residual-networks/logs/0.1/log.txt', 'parsers.torch.wide_resnet')
id2 = m.add_log('/home/prlz77/Code/wide-residual-networks/logs/0.01/log.txt', 'parsers.torch.wide_resnet')
id3 = m.add_log('/home/prlz77/Code/wide-residual-networks/logs/0.001/log.txt', 'parsers.torch.wide_resnet')
id4 = m.add_log('/home/prlz77/Code/wide-residual-networks/logs/0.0001/log.txt', 'parsers.torch.wide_resnet')
m.update()
m.multi_plot('epoch', ['test_acc'], [id,id2,id3,id4], legend=True)


