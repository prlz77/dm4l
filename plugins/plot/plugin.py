import StringIO
import logging
import urllib
from copy import deepcopy

import numpy as np

from misc import LogStatus
from plugins.abstract_plugin import AbstractPlugin
import matplotlib
#matplotlib.use('QT4Agg')
try:
    import seaborn as sns
except ImportError:
    logging.getLogger('dm4l').info('Install seaborn for nice looking plots.')
import pylab


class Plugin(AbstractPlugin):
    def __init__(self, dm4l, config):
        super(Plugin, self).__init__(dm4l, config)
        if self.config['frontend']:
            pylab.ioff()
            pylab.hold(True)

    def update(self, ids=None):
        pylab.cla()
        if len(self.dm4l.get_handlers().keys()) == 0:
            return True

        if ids is None:
            ids = self.dm4l.get_handlers().keys()
        else:
            ids = ids
        assert (type(self.config['y']) == list)
        assert (type(ids) == list)

        l_legend = []
        for handler_id in ids:
            if self.dm4l.get_handlers()[handler_id].status != LogStatus.ERROR:
                data = self.dm4l.get_handlers()[handler_id].get_data()
                x = np.array(data[self.config['x']])
                for y_field in self.config['y']:
                    y = self._process_y(np.array(data[y_field]))
                    pylab.plot(x, y)
                    pylab.xlabel(self.config['x'])
                    if len(set(self.config['y'])) == 1:
                        l_legend += [handler_id]
                    else:
                        l_legend += [y_field + ' ' + handler_id]
            else:
                return False

        if len(set(self.config['y'])) == 1:
            pylab.ylabel(y_field)
        if self.config['title'] is not None:
            pylab.title(self.config['title'])
        if self.config['y_min'] != 'auto':
            pylab.ylim(ymin=self.config['y_min'])
        elif self.config['y_max'] != 'auto':
            pylab.ylim(ymax=self.config['y_max'])
        if self.config['legend']:
            pylab.legend(l_legend).draggable()

        self._update_gui()
        return True

    def _process_y(self, y):
        y2 = y.copy()
        max_value = 100. / self.config['scale']
        y2 /= max_value
        if self.config['score'] == 'err':
            y2 = self.config['scale'] - y2

        return y2

    def _update_gui(self):
        if self.dm4l.refresh > 0:
            pylab.pause(0.0000001)
        else:
            pylab.show()

    def _get_img(self):
        imgdata = StringIO.StringIO()
        pylab.gcf().savefig(imgdata, format='png')
        imgdata.seek(0)  # rewind the data
        return 'data:image/png;base64,' + urllib.quote(base64.b64encode(imgdata.buf))

    def _save(self, path):
        pylab.savefig(path)