import logging
import StringIO
import numpy as np
from misc import LogStatus
import urllib
import matplotlib
from plugins.config import plot_conf
from copy import deepcopy
#matplotlib.use('TKAgg')
try:
    import seaborn as sns
except ImportError:
    logging.getLogger('dm4l').info('Install seaborn for nice looking plots.')
import pylab


class Plotter:
    def __init__(self, dm4l, frontend=True):
        if frontend:
            pylab.ioff()
        self.plot_params = deepcopy(plot_conf)
        self.dm4l = dm4l
        self.persistent = False
        self.prev_data = {}
        pylab.hold(True)

    def set_persistent(self, value):
        assert(type(value) == bool)
        self.persistent = value

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

    def update_gui(self):
        if not self.persistent:
            pylab.pause(0.0000001)
        else:
            pylab.show()

    def multi_plot(self, x_field, y_fields, handler_ids='all', title=None, plot_params={}):
        pylab.cla()
        if len(self.dm4l.get_handlers().keys()) == 0:
            return True

        if handler_ids == 'all':
            ids = self.dm4l.get_handlers().keys()
        else:
            ids = handler_ids
        assert (type(y_fields) == list)
        assert (type(ids) == list)
        for k in self.plot_params:
            if k not in plot_params:
                plot_params[k] = self.plot_params[k]

        l_legend = []
        for handler_id in ids:
            if self.dm4l.get_handlers()[handler_id].status != LogStatus.ERROR:
                data = self.dm4l.get_handlers()[handler_id].get_data()
                x = np.array(data[x_field])
                for y_field in y_fields:
                    y = self.process_y(np.array(data[y_field]))
                    pylab.plot(x, y)
                    pylab.xlabel(x_field)
                    if len(set(y_fields)) == 1:
                        l_legend += [handler_id]
                    else:
                        l_legend += [y_field + ' ' + handler_id]
            else:
                return False

        if len(set(y_fields)) == 1:
            pylab.ylabel(y_field)
        if title is not None:
            pylab.title(title)
        if plot_params['y_min'] != 'auto':
            pylab.ylim(ymin=plot_params['y_min'])
        elif plot_params['y_max'] != 'auto':
            pylab.ylim(ymax=plot_params['y_max'])
        if plot_params['legend']:
            pylab.legend(l_legend).draggable()

        return True

    def get_img(self):
        imgdata = StringIO.StringIO()
        pylab.gcf().savefig(imgdata, format='png')
        imgdata.seek(0)  # rewind the data
        return 'data:image/png;base64,' + urllib.quote(base64.b64encode(imgdata.buf))

    def save(self, path):
        pylab.savefig(path)