from plugins.abstract_plugin import AbstractPlugin
from bottle import Bottle, run
import Queue
from threading import Thread
from copy import deepcopy


def run_server(queue):
    app = Bottle()

    @app.route('/hello')
    def hello():
        data = None
        if not queue.empty():
            data = queue.get()

        return data

    run(app, host='localhost', port=8080)


class Plugin(AbstractPlugin):
    def __init__(self, dm4l, config):
        super(Plugin, self).__init__(dm4l, config)
        self.queue = Queue.Queue(maxsize=1)
        self.t = Thread(target=run_server, args=(self.queue,))
        self.t.setDaemon(True)
        self.t.start()

    def update(self, ids=None):
        handlers = self.dm4l.get_handlers()
        if ids is None:
            ids = handlers.keys()

        handlers_copy = {}
        for id in ids:
            handlers_copy[id] = deepcopy(handlers[id].log_data)

        if self.queue.full():
            with self.queue.mutex:
                self.queue.queue.clear()

        self.queue.put_nowait(handlers_copy)



