from plugins.abstract_plugin import AbstractPlugin
from bottle import Bottle, run, static_file
import Queue
from threading import Thread
from copy import deepcopy


def run_server(queue, config):
    import os
    import numpy as np
    os.chdir(os.path.dirname(__file__))
    app = Bottle()
    data = {}

    @app.route('/static/<filepath:path>')
    def server_static(filepath):
        return static_file(filepath, root='./templates/static')

    @app.route('/')
    def index():
        return static_file('report.html','./templates/')

    @app.get('/status')
    def status():
        if not queue.empty():
            new_data = queue.get()
            for id in new_data:
                data[id] = new_data[id]
        if data is not {}:
            data2 = {}
            for key in data:
                data2[key] = {}
                if 'epoch' in config['status_fields']:
                    data2[key]['epoch'] = str(data[key]['epoch'][-1])
                if 'test_acc' in config['status_fields']:
                    data2[key]['test_acc'] = str(data[key]['test_acc'][-1])
                if 'max_test_acc' in config['status_fields']:
                    data2[key]['test_acc'] = str(np.max(data[key]['test_acc'][-1]))
                if 'id' in 

                data2[key]['status'] = data[key]['status']
                if len(data[key]['epoch']) > 0:
                    data2[key]['epoch'] = str(data[key]['epoch'][-1])
                    data2[key]['test_acc'] = str(data[key]['test_acc'][-1])
                    data2[key]['max_acc'] = str(np.max(data[key]['test_acc']))
                else:
                    if data2[key]['status'] == 'TRAINING':
                        data2[key]['epoch'] = '0'
                        data2[key]['test_acc'] = '0'
                    else:
                        data2[key]['epoch'] = 'unknown'
                        data2[key]['test_acc'] = 'unknown'
            return data2
        else:
            return {}

    run(app, host='localhost', port=8080)


class Plugin(AbstractPlugin):
    def __init__(self, dm4l, config):
        super(Plugin, self).__init__(dm4l, config)
        self.queue = Queue.Queue(maxsize=1)
        self.t = Thread(target=run_server, args=(self.queue, deepcopy(self.config)))
        self.t.setDaemon(True)
        self.t.start()

    def update(self, ids=None):
        handlers = self.dm4l.get_handlers()
        if ids is None:
            ids = handlers.keys()

        handlers_copy = {}
        for id in ids:
            handlers_copy[id] = deepcopy(handlers[id].log_data)
            handlers_copy[id]['status'] = handlers[id].status

        if self.queue.full():
            with self.queue.mutex:
                self.queue.queue.clear()

        self.queue.put_nowait(handlers_copy)


