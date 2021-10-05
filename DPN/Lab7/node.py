import threading
import zlib
from time import sleep
from threading import Thread
from xmlrpc.server import SimpleXMLRPCServer
from xmlrpc.server import SimpleXMLRPCRequestHandler
import registry
import xmlrpc.client
URI_FRAME = "http://{}:{}"
DEFAULT_IP = "localhost"
DEFAULT_PATH = '/RPC2'
PROXY_URI = URI_FRAME.format(registry.DEFAULT_IP, registry.DEFAULT_PORT)
# Restrict to a particular path.


class RequestHandler(SimpleXMLRPCRequestHandler):
    rpc_paths = (DEFAULT_PATH,)


class MyXMLRPCServer(SimpleXMLRPCServer):
    def serve_forever(self):
        self.quit = 0
        while not self.quit:
            self.handle_request()

    def kill(self):
        self.quit = 1
        return 1


# my simple debugging tool
DEBUG = False


def log(*values):
    values = list(values)
    values.insert(0, "DEBUG >>")
    if(DEBUG):
        print(*values)


class Node(Thread):

    def __init__(self, port, m):
        threading.Thread.__init__(
            self, daemon=True, name='Node Thread <PORT>='+str(port))
        self.s = xmlrpc.client.ServerProxy(PROXY_URI)
        self.port = port
        self.m = m
        self.hash_table = []
        self.update_service_flag = True

    def _update_ft_pd(self):
        self.update_service_flag = True
        while self.update_service_flag:
            self.ft, self.predecessor_pair = self.s.populate_finger_table(
                self.id)
            log("Node port {0} finger tabel and predesessor updated.".format(
                self.port))
            log(self.ft)
            log(self.predecessor_pair)
            sleep(1)

    def _is_between(self, id, a, b):
        if a >= b:
            return True if (id <= b or id > a) else False
        elif b > a:
            return True if (id > a and id <= b) else False

    def _lookup(self, id):
        log("LOOK UP ID={0} at NODE {1}".format(id, self.id))
        if self._is_between(id, self.predecessor_pair[0], self.id): #check predecessor to id
            return (self.id, self.port)
        for i, key in enumerate(self.ft.keys()):
            if i==0: # check id to successor
                if self._is_between(id, self.id, int(key)):
                    return (int(list(self.ft.keys())[0]),
                            int(list(self.ft.values())[0]))
            elif i == len(self.ft)-1: # check if target ain't in ft 
                return (int(key), self.ft[key])
            elif self._is_between(id, int(key), int(list(self.ft.keys())[i+1])): # checking finger nodes pairwise
                return (int(list(self.ft.keys())[i]),
                        self.ft[list(self.ft.keys())[i]])
        return -1

    def handle_predecessor_loss(self, pd_ht):
        self.update_service_flag = False
        while self.update_ft_prd_thread.is_alive():
            pass
        self.hash_table += pd_ht
        self.ft, self.predecessor_pair = self.s.populate_finger_table(
            self.id)
        self.update_ft_prd_thread = Thread(
            target=self._update_ft_pd, daemon=True, name="FT-PD updater thread Node <PORT>="+str(self.port))
        self.update_ft_prd_thread.start()
        return True

    def handle_successor_loss(self):
        self.update_service_flag = False
        while self.update_ft_prd_thread.is_alive():
            pass
        self.ft, self.predecessor_pair = self.s.populate_finger_table(
            self.id)
        self.update_ft_prd_thread = Thread(
            target=self._update_ft_pd, daemon=True, name="FT-PD updater thread Node <PORT>="+str(self.port))
        self.update_ft_prd_thread.start()
        return True

    def run(self):
        respond = self.s.register(self.port)
        self.id = respond[0]
        if(respond[0] != -1):
            log(respond)
        else:
            log("ERROR REGISTERING NODE ", self.port)
        log("Node on port {0} running".format(self.port))
        sleep(1)
        self.update_ft_prd_thread = Thread(
            target=self._update_ft_pd, daemon=True, name="FT-PD updater thread Node <PORT>="+str(self.port))
        self.update_ft_prd_thread.start()

        self.server = MyXMLRPCServer(
            (DEFAULT_IP, self.port), requestHandler=RequestHandler, logRequests=False)

        self.server.register_function(self.get_finger_table)
        self.server.register_function(self.savefile)
        self.server.register_function(self.getfile)
        self.server.register_function(self.handle_predecessor_loss)
        self.server.register_function(self.handle_successor_loss)
        self.server.register_function(self.quit)

        self.server.serve_forever()

    def get_finger_table(self):
        self.update_service_flag = False
        while self.update_ft_prd_thread.is_alive():
            pass
        self.ft, self.predecessor_pair = self.s.populate_finger_table(self.id)
        self.update_ft_prd_thread = Thread(
            target=self._update_ft_pd, daemon=True, name="FT-PD updater thread Node <PORT>="+str(self.port))
        self.update_ft_prd_thread.start()
        log(self.ft)
        return self.ft

    def savefile(self, filename):

        hash_value = zlib.adler32(filename.encode())
        target_id = hash_value % 2**self.m

        try:
            target_node = self._lookup(target_id)
            if target_node == -1:
                    raise SystemError('Failed to look-up the chord')
            if target_node[0] == self.id:
                if hash_value in self.hash_table:
                    return [False, '{0} already exists in Node {1}'.format(filename, self.id)]
                else:
                    self.hash_table.append(hash_value)
                    return [True, '{0} is saved in Node {1}'.format(filename, self.id)]
            print('node {0} passed {1} to node {2}'.format(
                self.id, filename, target_node[0]))
            otherNode = xmlrpc.client.ServerProxy(
                URI_FRAME.format(DEFAULT_IP, target_node[1]))
            return otherNode.savefile(filename)
        except Exception as ex:
            return [False, 'FAILED NODE <ID><PORT>={}'.format(target_node)]

    def getfile(self, filename):
        hash_value = zlib.adler32(filename.encode())
        target_id = hash_value % 2**self.m

        try:
            target_node = self._lookup(target_id)
            if target_node == -1:
                raise SystemError('Failed to look-up the chord')
            if target_node[0] == self.id:
                if hash_value in self.hash_table:
                    return [True, 'Node {0} has {1}'.format(self.id, filename)]
                else:
                    self.hash_table.append(hash_value)
                    return [False, 'Node {0} doesn’t have the {1}'.format(self.id, filename)]
            print('node {0} passed {1} to node {2}'.format(
                self.id, filename, target_node[0]))
            otherNode = xmlrpc.client.ServerProxy(
                URI_FRAME.format(DEFAULT_IP, target_node[1]))
            return otherNode.getfile(filename)
        except Exception as ex:
            return [False, 'FAILED NODE <ID><PORT>={}'.format(target_node)]

    def quit(self):
        self.update_service_flag = False
        while self.update_ft_prd_thread.is_alive():
            pass
        respond = self.s.deregister(self.id)
        if respond[0] == True:
            respond = [True,'Node {0} with port {1} was deregistered'.format(self.id,self.port)]
        successor = ()
        for first_item in self.ft.items():
            successor = first_item
            break

        # notifing successor
        try:
            otherNode = xmlrpc.client.ServerProxy(
                URI_FRAME.format(DEFAULT_IP, successor[1]))
            otherNode.handle_predecessor_loss(self.hash_table)
        except Exception as ex:
            return [False, 'FAILED NOTIFING NODE <ID><PORT>={}'.format(successor)]

        # notifing predecessor
        try:
            otherNode = xmlrpc.client.ServerProxy(
                URI_FRAME.format(DEFAULT_IP, self.predecessor_pair[1]))
            otherNode.handle_successor_loss()
            self.server.kill()
            return respond
        except Exception as ex:
            return [False, 'FAILED NOTIFING NODE <ID><PORT>={}'.format(successor)]
