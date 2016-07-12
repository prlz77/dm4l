from handlers.abstract_log_handler import AbstractLogHandler, HandlerStatus


class LogHandler(AbstractLogHandler):
    def __init__(self, log_path):
        super(LogHandler, self).__init__(log_path)

        self.handler_settings['skip_header'] = True

        self.solver_params = None
        self.buffer = ""
        self.epoch = 1

    def parse(self):
        changed = False
        self.buffer += self.fp.read()
        if self.buffer != '':
            buffer_list = self.buffer.split('\n')
            if self.handler_settings['skip_header']:
                self.handler_settings['skip_header'] = False
                if len(buffer_list) == 1:
                    buffer_list = []
                else:
                    buffer_list = buffer_list[1:]
            self.buffer = ''

            for l in buffer_list:
                if self.status != HandlerStatus.TRAINING:
                    self.status = HandlerStatus.TRAINING
                if 'test_acc' not in self.log_data and l != '':
                    self.log_data['test_acc'] = [float(l)]
                    self.log_data['epoch'] = [self.epoch]
                    changed = True
                elif l != '':
                    self.log_data['test_acc'] += [float(l)]
                    self.log_data['epoch'] += [self.epoch]
                    changed = True

                self.epoch += 1
        return changed

    def get_data(self):
        return self.log_data