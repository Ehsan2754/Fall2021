from os import pipe
from multiprocessing import Process, Pipe
from threading import Thread
import sys
from time import sleep
import xmlrpc.client
import registry
from registry import Registry
from node import Node

PROXY_URI = "http://{}:{}".format(registry.DEFAULT_IP, registry.DEFAULT_PORT)
NODE_URI = "http://localhost:{}"

INIT_MSG = "Registry and {} nodes are created"
# my simple debugging tool
DEBUG = False


def log(*values):
    values = list(values)
    values.insert(0, "DEBUG >>")
    if(DEBUG):
        print(*values)
# Interrupt Handles


def detect_interrupt(conn):
    try:
        while True:
            pass
    except KeyboardInterrupt:
        conn.send(True)
        conn.close()


def listen_for_interrupt(conn,):
    conn.recv()

# evaluation of input arguments regarding port range and input types


def eval_args(args):
    if not args:
        raise ValueError("NO INPUT ARGUMENTs")
    for item in args:
        if not item.isnumeric():
            raise ValueError("INPUT ARGUMENTs should be numeric!")
    if len(args) == 2:
        if(0 < eval(args[1]+"-"+args[0])) and (eval(args[1]+"-"+args[0]) < 2**5):
            args.insert(0, '5')
            return list(map(int, args))
        raise ValueError("BAD INPUT PORT RANGE")
    if len(args) == 3:
        if(0 <= eval(args[2]+"-"+args[1]) and eval(args[2]+"-"+args[1]) < eval("2**"+args[0])):
            return list(map(int, args))
        raise ValueError("BAD INPUT PORT RANGE")
    else:
        raise ValueError("BAD INPUT ARGUMENT")


if __name__ == "__main__":
    try:
        # main_conn, detect_conn = Pipe()
        # listen_for_interrupt_thread = Thread(
        #     target=listen_for_interrupt, args=(main_conn,), daemon=True)
        # listen_for_interrupt_thread.start()
        # detect_interrupt_process = Process(
        #     target=detect_interrupt, args=(detect_conn,))
        # detect_interrupt_process.start()

        # evaluate input
        CORD_BITS, START_PORT, END_PORT = (eval_args(sys.argv[1:]))
        r = Registry(m=CORD_BITS,startPort=START_PORT,endPort=END_PORT)
        r.start()
        # create the registery and nodes
        log("ChordBits=", CORD_BITS, "\tStartPort=",
            START_PORT, "\tEndPorts=", END_PORT)
        s = xmlrpc.client.ServerProxy(PROXY_URI)
        nodes = []
        for nodePort in range(START_PORT,END_PORT+1,1):
            nodes.append(Node(nodePort))
        for node in nodes:
            node.start()
            # sleep(0.5)
        print(INIT_MSG.format(END_PORT-START_PORT+1))
        # print("type 'quit' to exit the program'")
        input_ = input(">")    
        while(input_ != "quit"):
            if input_ == 'get_chord_info':
                res = s.get_chord_info()
                print(res)
            if (len(input_.split())==2):
                if(input_.split()[0] == 'get_finger_table') and (input_.split()[1].isnumeric()):
                    res=None
                    in_port = int(input_.split()[1])
                    log(in_port)
                    node = xmlrpc.client.ServerProxy(NODE_URI.format(in_port))
                    res = node.get_finger_table()
                    print(res)
                    
            input_ = input(">")

    except KeyboardInterrupt as KI:
        print(KI)

    except Exception as ex:
        log(ex)
    finally:
        r.join()
        # detect_interrupt_process.terminate()
        exit()
