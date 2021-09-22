from functools import cache
from threading import Thread
import threading
from xmlrpc.server import SimpleXMLRPCServer
from xmlrpc.server import SimpleXMLRPCRequestHandler
import random

DEFAULT_IP = "localhost"
DEFAULT_PORT = 8080
DEFAULT_PATH = '/RPC2'


# my simple debugging tool
DEBUG = False


def log(*values):
    values = list(values)
    values.insert(0, "DEBUG >>")
    if(DEBUG):
        print(*values)


class Registry(Thread):
    CHORD_IS_FULL_MSG = "there are already 2**m nodes given that m is the identifier length in bits"
    PORT_NOT_IN_RANGE_MSG = "requested port {0} to register is not in range of granted ports"
    DEREG_MSG = "Successfully deregistering of the node{0}"
    DEREG_ERR = "no such id {0} exists in dict of registered nodes"
    nodes = {}

    def __init__(self, m, startPort, endPort, group=None, target=None, name=None, args=None, kwargs=None, *, daemon=True) -> None:

        self.m = m
        self.startPort = startPort
        self.endPort = endPort
        random.seed(0)

        threading.Thread.__init__(self)
        log("Registry Object Created")

    def run(self):
        try:
            log("REGISTRY RUNNING")

            server = SimpleXMLRPCServer((DEFAULT_IP, DEFAULT_PORT), logRequests=False) 
            # server.register_instance(Registry())
            # server.register_introspection_functions()
            server.register_function(self.register)
            server.register_function(self.deregister)
            server.register_function(self.get_chord_info)
            server.register_function(self.populate_finger_table)
            server.serve_forever()
        finally:
            # Avoid a refcycle if the thread is running a function with
            # an argument that has a member that points to the thread.
            del self._target, self._args, self._kwargs

    def _getIDs(self):
        return self.nodes.keys()

    def _getPorts(self):
        return self.nodes.values()

    def _isChordFull(self):
        return len(self.nodes) == 2**self.m

    def _inPortRange(self, port):
        return (
            port >= self.startPort and port <= self.endPort
        )

    def _getSuccessor(self, id):
        id = id % (2 ** self.m)
        try:
            for i in range(id, 2 ** self.m):
                if i in self.nodes.keys():
                    return i
            for i in range(id):
                if i in self.nodes:
                    return i
            return -1
        except Exception as ex:
            log(ex)

    def _getNewID(self):
        newID = -1
        while newID==-1:
            newID = random.randint(0,2**self.m-1)
            if newID in self.nodes.keys():
                newID = -1
        return newID

    def register(self, port):
        try:
            log("REQ REG:\t", port)
            if self._isChordFull():
                return(-1, self.CHORD_IS_FULL_MSG)
            if not self._inPortRange(port):
                return(-1, self.PORT_NOT_IN_RANGE_MSG.format(port))
            newID = self._getNewID()
            self.nodes[newID] = port
            return(newID, len(self.nodes))
        except Exception as ex:
            return (-1, str(ex))

    def deregister(self, id):
        log("REQ DREG:\t", id)
        if(self.nodes.get(id, None)):
            self.nodes.pop(id)
            return(True, self.DEREG_MSG.format(id))
        return(False, self.DEREG_MSG.format(self.DEREG_ERR.format(id)))

    def get_chord_info(self):
        log("SENDING CHORD")
        chord = {str(key): self.nodes[key] for key in self.nodes.keys()}
        return chord

    def populate_finger_table(self, id):
        try:
            log("GENERATING FT-ID{}".format(id))
            fingerTable = {}
            for i in range(self.m):
                fingerID = self._getSuccessor(id+2**i)
                log(fingerID)
                if (not (fingerID == -1)) and (not fingerID == id):
                    fingerTable[str(fingerID)] = self.nodes[fingerID]
            return (fingerTable)
        except Exception as ex:
            raise ex
