import threading
from time import sleep
from threading import Thread
from xmlrpc.server import SimpleXMLRPCServer
from xmlrpc.server import SimpleXMLRPCRequestHandler
import registry
import xmlrpc.client
DEFAULT_IP = "localhost"
DEFAULT_PATH = '/RPC2'
PROXY_URI = "http://{}:{}".format(registry.DEFAULT_IP, registry.DEFAULT_PORT)


# my simple debugging tool
DEBUG = False


def log(*values):
    values = list(values)
    values.insert(0, "DEBUG >>")
    if(DEBUG):
        print(*values)


class Node(Thread):

    def __init__(self, port):
        threading.Thread.__init__(self)
        self.s = xmlrpc.client.ServerProxy(PROXY_URI)
        self.port = port

    def run(self):
        respond = self.s.register(self.port)
        self.id = respond[0]
        sleep(1)
        self.ft = self.s.populate_finger_table(self.id)
        log("Node port {0} initiated.".format(self.port))
        if(respond[0] != -1):
            log(respond)

        else:
            log("ERROR REGISTERING NODE ", self.port)
        log("Node on port {0} running".format(self.port))
        
        server = SimpleXMLRPCServer((DEFAULT_IP, self.port), logRequests=False) 
        # server.register_introspection_functions()
        server.register_function(self.get_finger_table)
        server.register_function(self.quit)
        server.serve_forever()

    def get_finger_table(self):
        self.s.populate_finger_table(self.id)
        log(self.ft)
        return self.ft

    def quit(self):
        respond = self.s.deregister(self.id)
        return respond
