import logging
from logging import debug
logging.basicConfig( encoding='utf-8', level=logging.DEBUG)
from constants import *

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


if __name__ == '__main__':
    nodes = parseConf(CONFIG_PATH)

    debug(nodes)
