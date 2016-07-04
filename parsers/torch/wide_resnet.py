import json
from abstract_parser import AbstractParser
from misc import LogStatus

def match(start_symbol, end_symbol, buffer):
    counter = 0
    iter = 0
    start_iter = -1
    end_iter = -1
    while (iter == 0 or counter > 0 or start_iter == -1) and iter < len(buffer):
        if buffer[iter] == start_symbol:
            if counter == 0:
                start_iter = iter
            counter +=1
        elif buffer[iter] == end_symbol:
            counter -= 1
            if counter == 0:
                end_iter = iter
        iter += 1
    return start_iter, end_iter

class Parser(AbstractParser):
    def __init__(self, log_path, settings={}):
        super(Parser, self).__init__(log_path)
        self.solver_params = None
        self.buffer = ""

    def _update(self):
        self.buffer += self.fp.read().replace('\t','')
        line = ''
        buffer_list = self.buffer.split('\n')
        for l in buffer_list:
            if 'json_stats' in l:
                line = l
                if self.status != LogStatus.TRAINING:
                    self.status = LogStatus.TRAINING
                if l[-1] == '}':
                    data = json.loads(l[l.find('{'):])
                    for field in data:
                        if field not in self.log_data:
                            self.log_data[field] = [data[field]]
                        else:
                            self.log_data[field] += [data[field]]
        if line != '':
            if line[-1] == '}':
                self.buffer = ''
            elif line != '':
                self.buffer = line



    def get_data(self):
        return self.log_data


