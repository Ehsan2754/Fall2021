from os import pipe
from multiprocessing import Process, Pipe
from threading import Thread
import sys,zlib
from time import sleep
import xmlrpc.client
import registry
from registry import Registry
from node import Node

PROXY_URI = "http://{}:{}".format(registry.DEFAULT_IP, registry.DEFAULT_PORT)
NODE_URI = "http://localhost:{}"

INIT_MSG = "Registry and {} nodes are created"
INVALID_COMMAND_MSG = '''
!!! ERROR:\t INVALID COMMAND.
\tYou may enter the following commands to the prompt:
\t  > get_chord_info
\t\t displays the current scheme of the chord
\t  > get_finger_tabel <PORT>
\t\t prints the current finger print of the node on the input arguement <PORT>
\t  > save <PORT> <FILENAME>
\t\t Requests from the node running on <PORT> to save <FILENAME> in the cord
\t  > get <PORT> <FILENAME>
\t\t Requests from the node running on <PORT> to get <FILENAME> in the cord
\t  > quit <PORT>
\t\t Deregisters and removes the node running on <PORT> from the chord
!CAUTION : MAKE SURE YOUR INPUT ARGUMENTS DOESN'T CONTAIN SPACE
Enter 'quit' or 'CTRL+C' to exit the program
'''
# my simple debugging tool
DEBUG = False


def log(*values):
    values = list(values)
    values.insert(0, "DEBUG >>")
    if(DEBUG):
        print(*values)




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
        # evaluate input
        CORD_BITS, START_PORT, END_PORT = (eval_args(sys.argv[1:]))
        r = Registry(m=CORD_BITS, startPort=START_PORT, endPort=END_PORT)
        r.start()
        # create the registery and nodes
        log("ChordBits=", CORD_BITS, "\tStartPort=",
            START_PORT, "\tEndPorts=", END_PORT)
        s = xmlrpc.client.ServerProxy(PROXY_URI)
        nodes = []
        for nodePort in range(START_PORT, END_PORT+1, 1):
            nodes.append(Node(nodePort,CORD_BITS))
        for node in nodes:
            node.start()
        print(INIT_MSG.format(END_PORT-START_PORT+1))
        print("Enter 'quit' or 'CTRL+C' to exit the program")
        input_ = input(">")
        while(input_ != "quit"):

            if input_ == 'get_chord_info':    # config for 'get_chord_info' command
                res = s.get_chord_info()
                print(res)

            elif (len(input_.split()) == 2):      # config for commands with 1 argument
                # get_finger_tabel cmd
                if(input_.split()[0] == 'get_finger_table') and (input_.split()[1].isnumeric()):
                    res = None
                    in_port = int(input_.split()[1])
                    log(in_port)
                    node = xmlrpc.client.ServerProxy(NODE_URI.format(in_port))
                    res = node.get_finger_table()
                    print(res)
                # quit <port> cmd
                if(input_.split()[0] == 'quit') and (input_.split()[1].isnumeric()):
                    res = None
                    in_port = int(input_.split()[1])
                    log(in_port)
                    node = xmlrpc.client.ServerProxy(NODE_URI.format(in_port))
                    res = node.quit()
                    print(res)

            elif (len(input_.split()) == 3):      # config for commands with 2 argument
                # save <port> <filename> cmd
                log(input_.split())
                if(input_.split()[0] == 'save') and (input_.split()[1].isnumeric()):
                    res = None
                    in_port = int(input_.split()[1])
                    file_name= input_.split()[2]
                    hash_value = zlib.adler32(file_name.encode())
                    identifier = hash_value % 2**CORD_BITS
                    print('{0} has identifier {1}'.format(file_name,identifier))
                    node = xmlrpc.client.ServerProxy(NODE_URI.format(in_port))
                    res = node.savefile(file_name)
                    print(res)
                # get <port> <filename> cmd
                if(input_.split()[0] == 'get') and (input_.split()[1].isnumeric()):
                    res = None
                    in_port = int(input_.split()[1])
                    file_name= input_.split()[2]
                    # hash_value = zlib.adler32(file_name.encode())
                    # identifier = hash_value % 2**CORD_BITS
                    # print('{0} has identifier {1}'.format(file_name,identifier))
                    node = xmlrpc.client.ServerProxy(NODE_URI.format(in_port))
                    res = node.getfile(file_name)
                    print(res)
            else:
                print(INVALID_COMMAND_MSG)

            input_ = input(">")

    except KeyboardInterrupt as KI:
        print(KI)

    except Exception as ex:
        print('!!! Error: ',type(ex))
        log(ex)
    finally:
        exit()
