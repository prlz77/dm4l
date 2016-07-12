from plugins.abstract_plugin import AbstractPlugin
from bottle import Bottle, run, static_file, template
import Queue
from threading import Thread
from copy import deepcopy


class Namespace():  #  workarround to access parent variables
    pass

def run_server(queue, config):
    import os
    import numpy as np
    os.chdir(os.path.dirname(__file__))
    app = Bottle()
    data = {}
    namespace = Namespace()
    namespace.config = config

    @app.route('/static/<filepath:path>')
    def server_static(filepath):
        return static_file(filepath, root='./templates/static')

    @app.route('/')
    def index():
        with open('./templates/report.html','r') as input:
            txt = input.read()
        return template(txt, **namespace.config)


    @app.get('/status')
    def status():
        if not queue.empty():
            new_data = queue.get()
            for id in new_data:
                data[id] = new_data[id]
        if data is not {}:
            data2 = {'data':[]} #DataTables format
            for key in data:
                data2['data'].append({})
                for field in config['status_fields']:
                    if field == 'id':
                        data2['data'][-1][field] = key
                    elif field == 'max_acc':
                        if len(data[key]['test_acc']) == 0:
                            data2['data'][-1][field] = 'Null'
                        else:
                            data2['data'][-1][field] = str(np.max(data[key]['test_acc']))
                    elif isinstance(data[key][field], list):
                        if len(data[key][field]) > 0:
                            data2['data'][-1][field] = str(data[key][field][-1])
                        else:
                            data2['data'][-1][field] = 'Null'
                    else:
                        data2['data'][-1][field] = str(data[key][field])
            print data2
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


