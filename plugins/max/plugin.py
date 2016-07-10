from plugins.abstract_plugin import AbstractPlugin
import numpy as np


class Plugin(AbstractPlugin):
    def __init__(self, dm4l, config):
        super(Plugin, self).__init__(dm4l, config)

    def update(self, ids=None):
        """ Get the max score value from a log or log list.

        :param handler_ids: list of the log ids to compare.
        :param value_field: metric to compare.
        :return: (max value, argmax value, id)
        """
        handlers = self.dm4l.get_handlers()
        if ids == None:
            ids = handlers.keys()
        assert(isinstance(ids, list))
        max_list = np.zeros(len(ids))
        arg_list = np.zeros(len(ids))
        for i, handler_id in enumerate(ids):
            y = handlers[handler_id].log_data[self.config['value_field']]
            if len(y) > 0:
                max_list[i] = np.max(y)
                arg_list[i] = np.argmax(y)
            else:
                max_list[i] = -np.inf
                arg_list[i] = -1

        max = np.max(max_list)
        id = ids[np.argmax(max_list)]
        arg = arg_list[np.argmax(max_list)]
        if self.config['print']:
            res = [max, arg, id]
            print ' '.join([str(res[x]) for x in self.config['format']])
        return max, arg, id