from abstract_parser import AbstractParser
from misc import LogStatus

class Parser(AbstractParser):
    def __init__(self, log_path):
        super(Parser, self).__init__(log_path)

        self.parser_settings['skip_header'] = True

        self.solver_params = None
        self.buffer = ""
        self.epoch = 1

    def _update(self):
        self.buffer += self.fp.read()
        if self.buffer != '':
            buffer_list = self.buffer.split('\n')
            if self.parser_settings['skip_header']:
                if len(buffer_list) == 1:
                    buffer_list = []
                else:
                    buffer_list = buffer_list[1:]
            self.buffer = ''

            for l in buffer_list:
                if self.status != LogStatus.TRAINING:
                    self.status = LogStatus.TRAINING
                if 'test_acc' not in self.log_data and l != '':
                    self.log_data['test_acc'] = [float(l)]
                    self.log_data['epoch'] = [self.epoch]
                elif l != '':
                    self.log_data['test_acc'] += [float(l)]
                    self.log_data['epoch'] += [self.epoch]

                self.epoch += 1

    def get_data(self):
        return self.log_data