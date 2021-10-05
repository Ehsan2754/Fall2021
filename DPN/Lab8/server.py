# configuring my log env
import logging
from logging import debug
logging.basicConfig( encoding='utf-8', level=logging.DEBUG)
# other imports
import threading
from constants import *

# Parses the configuration file
def parseConf(path):
    EMPTY_LINE = ''
    pairs = {}
    CONF = open(path, 'r')
    line = CONF.readline()
    while(line):
        node = line.split()
        pairs[int(node[0])] = (node[1], int(node[2]))
        line = CONF.readline()
    CONF.close()
    return pairs



class Node(threading.Thread):
    TIME_RANGE = (150,300)

    def __init__(self,id,addr_port_pair):
        self.term_number = 0
        self.id = id
        self.addr_port_pair = addr_port_pair
        name = f'Node{str(id)}:<{str(addr_port_pair)}>'
        super().__init__(name=name,daemon=True)
    def run(self) -> None:
        return super().run()



if __name__ == '__main__':
    nodes = parseConf(CONFIG_PATH)
    debug(nodes)

