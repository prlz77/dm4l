from plugins.abstract_plugin import AbstractPlugin
from bottle import Bottle, run, static_file, template, request
import Queue
from threading import Thread
from copy import deepcopy


class Namespace():  #  workarround to access parent variables
    pass


def run_server(recv_queue, config):
    import os
    import numpy as np
    os.chdir(os.path.dirname(__file__))
    app = Bottle()
    data = {}
    namespace = Namespace()
    namespace.config = config
    ids = {}
    id_counter = [1]  # make it mutable
    selections = []
    handlers = {}
    old_plot_data = {}
    plot_fields = ['epoch','test_acc']

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
        if not recv_queue.empty():
            new_data = recv_queue.get()
            for id in new_data:
                data[id] = deepcopy(new_data[id])  # mutabe
        if data is not {}:
            data2 = {'data':[]} #DataTables format
            for key in data:
                data2['data'].append({})
                for field in config['status_fields']:
                    if field == 'id':
                        if key not in ids:
                            ids[key] = id_counter[0]
                            id_counter[0] += 1
                        data2['data'][-1][field] = ids[key]
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
            for key in range(len(data2['data'])):
                for field in data2['data'][key]:
                    if isinstance(data2['data'][key][field], str):
                        data2['data'][key][field] = "<div class='add-overflow'> %s </div>" %data2['data'][key][field]
            return data2
        else:
            return {}

    @app.post('/select')
    def select():
        id = request.forms.get('id')
        while len(selections) != 0:
            selections.pop()
        if id is None:
            id = []
        print id
        for key in ids:  # ugly
            for i in id:
                if int(ids[key]) == int(i):
                    selections.append(key)


    @app.get('/update_plot_data')
    def update_plot_data():
        if not recv_queue.empty():
            new_plot_data = recv_queue.get()
        else:
            new_plot_data = handlers
        ret = {}
        for key in selections:
            if key in new_plot_data:
                if key in old_plot_data:
                    ret[key] = {}
                    for field in new_plot_data:
                        if isinstance(new_plot_data[key][field], list):
                            if len(new_plot_data[key][field]) > len(old_plot_data[key][field]):
                                ret[key][field] = new_plot_data[key][field][len(old_plot_data[key][field]):]
                            else:
                                ret[key][field] = []



        return ret

    @app.get('/get_plot_data')
    def get_plot_data():
        if not recv_queue.empty():
            new_plot_data = recv_queue.get()
            for id in data:
                data[id] = deepcopy(new_plot_data[id])
        head=','.join(['epoch'] + selections)+'\n'

        min_epoch = np.inf
        max_epoch = -np.inf
        for i, id in enumerate(selections):
            if len(data[id]['epoch']) > 0:
                print np.min([min_epoch, data[id]['epoch'][0]])
                print np.max([max_epoch, data[id]['epoch'][-1]])
                min_epoch = int(np.min([min_epoch, data[id]['epoch'][0]]))
                max_epoch = int(np.max([max_epoch, data[id]['epoch'][-1]]))

        if min_epoch < np.inf and max_epoch > -np.inf:
            datapoints = [[str(epoch)] + ['null']*len(selections) for epoch in range(int(min_epoch), int(max_epoch+1))]

            for i, id in enumerate(selections):
                for j, epoch in enumerate(data[id]['epoch']):
                    datapoints[epoch - min_epoch][i + 1] = str(data[id]['test_acc'][j])
            datapoints = [','.join(x) for x in datapoints ]
            datapoints = '' + head + '\n'.join(datapoints) + ''
        else:
            datapoints = '"' + head + '"'
        return datapoints








    run(app, host='localhost', port=8080, server="cherrypy")


class Plugin(AbstractPlugin):
    def __init__(self, dm4l, config):
        super(Plugin, self).__init__(dm4l, config)
        self.queue = Queue.Queue(maxsize=1)  # sends log status to thread
        self.t = Thread(target=run_server, args=(self.queue, deepcopy(self.config)))
        self.t.setDaemon(True)
        self.t.start()

    def update(self, ids=None):
        handlers = self.dm4l.get_handlers()
        if ids is None:
            ids = handlers.keys()

        # Gather status data
        handlers_copy = {}
        for id in ids:
            handlers_copy[id] = deepcopy(handlers[id].log_data)
            handlers_copy[id]['status'] = handlers[id].status
            handlers_copy[id]['log_path'] = handlers[id].log_path
        # send to thread
        if self.queue.full():
            with self.queue.mutex:
                self.queue.queue.clear()
        self.queue.put_nowait(handlers_copy)





