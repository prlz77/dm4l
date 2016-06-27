from parser import Parser
import json

class WideResnet(Parser):
    def __init__(self, log_path):
        with open(log_path, 'r') as logfp:
            self.list_data = logfp.readlines()
        self.log_data = {}
        for l in self.list_data:
            if 'json_stats' in l:
                data = json.loads(l[l.find('{'):])
                for field in data:
                    if field not in self.log_data:
                        self.log_data[field] = [data[field]]
                    else:
                        self.log_data[field].append(data[field])
    def get_data(self):
        return self.log_data

w = WideResnet('/Users/prlz77/Code/wide-resnet/0.0001/log.txt')

