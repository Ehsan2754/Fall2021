from enum import Flag
import sys,os
from multiprocessing import Pipe, Process
from threading import Thread
import xmlrpc.client
import pickle


ip = "127.0.0.1"
port = 6000
SERVER_URL="http://{0}:{1}"
PATH = os.path.dirname(os.path.realpath(__file__)) + "/CLIENT_FILES"
BAD_ARG_MSG = """Usage example: python ./client.py <address> <port>"""
ENTER_MSG = "\nEnter the command:"
KI_MSG = "KeyboardInterrupt"
EXIT_MSG = "Client is stopping"
COMELETED_MSG = "Completed"
NOT_COMPELETED_MSG = "Not completed"
WRONG_COMMAND_MSG = "Wrong command"
WRONG_FILE_MSG = "No such file"
EXISTING_FILE_MSG = "File already exists"
WRONG_EXPR_CMD = "Wrong expression"
DEVISION_BY_ZERO_MSG = "Division by zero"

QUIT_CMD = ("quit",)
SEND_CMD = ("send","<filename>")
LIST_CMD = ("list",)
DELETE_CMD = ("delete", "<filename>")
GET_CMD = ("get" ,"<filename>" ,"<new filename>")
CALC_CMD = ("calc" ,"<expression>")
EXPRESSION = ("OPERATOR","LEFT_OPERAND","RIGHT_OPERAND")
CMD_DICT={
    QUIT_CMD[0]:QUIT_CMD[1:],
    SEND_CMD[0]:SEND_CMD[1:],
    LIST_CMD[0]:LIST_CMD[1:],
    DELETE_CMD[0]:DELETE_CMD[1:],
    GET_CMD[0]:GET_CMD[1:],
    CALC_CMD[0]:EXPRESSION
}

TIMEOUT = 5.0
BUFFERSIZE = 2048
FULLSERVER_MSG = """The server is full"""
SERVER_NA_MSG = """Server is unavailable"""
CNNLOSS_MSG = """Connection lost"""


def detect_interrupt(conn):
    try:
        while True:
            pass
    except KeyboardInterrupt:
        conn.send(True)
        conn.close()


def listen_for_interrupt(conn, sock=None):
    conn.recv()
    # sock.close()


def eval_args(input):
    # checking length of arguments
    ARGLEN_FLG = len(input) == 2
    if not ARGLEN_FLG:
        print(WRONG_COMMAND_MSG)
        print(BAD_ARG_MSG)
        exit()
    # checing if the ip addr is a valid IPv4
    IP_FLG = len(input[0].split(".")) == 4
    # checing it the address is valid
    for block in input[0].split("."):
        IP_FLG = IP_FLG and block.isnumeric()
    if input[0] == 'localhost':
        IP_FLG=True
    PORT_FLG = input[1].isnumeric()
    if not (IP_FLG and PORT_FLG):  # Handles bad input
        print(WRONG_COMMAND_MSG)
        print(BAD_ARG_MSG)
        exit()
    return input[0],input[1]

def eval_input(input):
    FLG=False
    cmd=input.split()
    if(cmd):
        if cmd[0] in CMD_DICT.keys():
            if cmd[0] == QUIT_CMD[0] or cmd[0] == LIST_CMD[0]:
                return[cmd[0]]
            if cmd[0] == SEND_CMD[0] or cmd[0] == DELETE_CMD[0]:
                if len(cmd)>=2:
                    return cmd[:2]
            if cmd[0] == GET_CMD[0]:
                if len(cmd) == 2:
                    return cmd
                if len(cmd) > 2:
                    return cmd[:3]
            if cmd[0] == CALC_CMD[0]:
                if len(cmd)==4:
                    return cmd
    raise Exception(WRONG_COMMAND_MSG,cmd)
    
            
def proxyRun(ServerProxy,CMD):
    ServerProxyStr=''
    for name in globals():
        if eval(name) == ServerProxy:
            ServerProxyStr=name
    if CMD[1:]:
        return eval(ServerProxyStr+'.'+CMD[0]+'(*'+str(CMD[1:])+')')
    else:
        return eval(ServerProxyStr+'.'+CMD[0]+'()')


if __name__ == "__main__":
    try:
        # HANDLE KI PARALLEL
        # Crate a Pipe for IPC
        main_conn, detect_conn = Pipe()
        # Create a thread in main process to listen on connection
        listen_for_interrupt_thread = Thread(
            target=listen_for_interrupt, args=(main_conn,), daemon=True)
        listen_for_interrupt_thread.start()
        # Create a separate process to detect the KeyboardInterrupt
        detect_interrupt_process = Process(
            target=detect_interrupt, args=(detect_conn,))
        detect_interrupt_process.start()
        ip,port = eval_args(sys.argv[1:])  # getting and evaluating user input args
        # CREATING CLIENT FILE DIRECTORY 
        if not os.path.isdir(PATH):
            os.mkdir(PATH)

        s = xmlrpc.client.ServerProxy(SERVER_URL.format(ip,port))

        while True:
            try:
                USER_INPUT = input(ENTER_MSG)
                CMD=eval_input(USER_INPUT)
                if CMD[0] == QUIT_CMD[0]:        # quit   command handling
                    break  
                elif CMD[0] == SEND_CMD[0]:      # send   command handling
                    try:                        
                        output_file_path = PATH + "/" + CMD[1]
                        if not os.path.isfile(PATH + "/" + CMD[1]): # checks if the file is on client
                            print(NOT_COMPELETED_MSG)
                            print(WRONG_FILE_MSG)
                            continue
                        with open(output_file_path, "rb") as handle:
                            data = handle.read()
                        CMD.append(data)
                        RESULT = proxyRun(s,CMD)
                        if RESULT == False:
                            print(NOT_COMPELETED_MSG)
                            print(EXISTING_FILE_MSG)
                            continue
                        print(COMELETED_MSG)
                    except Exception as ex:
                        raise ex
                elif CMD[0] == LIST_CMD[0]:      # list   command handling
                    RESULT=proxyRun(s,CMD)
                    if RESULT == False:
                        print(NOT_COMPELETED_MSG)
                        continue
                    for file in RESULT:
                        print(file)
                    print(COMELETED_MSG)
                elif CMD[0] == DELETE_CMD[0]:    # delete command handling
                    RESULT=proxyRun(s,CMD)
                    if RESULT == False:
                        print(NOT_COMPELETED_MSG)
                        print(WRONG_FILE_MSG)
                        continue
                    print(COMELETED_MSG)
                elif CMD[0] == GET_CMD[0]:       # get    command handling
                    try:                        
                        output_file_path = PATH + "/" + CMD[1] if len(CMD)==2 else PATH + "/" + CMD[2] # handles if the command has 2 arguments
                        if os.path.isfile(PATH + "/" + CMD[1]): # checks if the file is on client
                            print(NOT_COMPELETED_MSG)
                            print(EXISTING_FILE_MSG)
                            continue
                        RESULT = proxyRun(s,CMD[:2])
                        if RESULT == False:
                            print(NOT_COMPELETED_MSG)
                            print(WRONG_FILE_MSG)
                            continue
                        data=RESULT.data
                        with open(output_file_path, "wb") as handle:
                            handle.write(data)
                            print(COMELETED_MSG)
                    except Exception as ex:
                        raise ex
                elif CMD[0] == CALC_CMD[0]:      # calc   command handling
                    RESULT=proxyRun(s,CMD)
                    if RESULT[0] == False:
                        print(NOT_COMPELETED_MSG)
                        for item in RESULT[1:]:
                            print(item)
                        continue
                    print(RESULT[1])
                    print(COMELETED_MSG)
                
                
                
            except Exception as ex:
                if ex.args:
                    if ex.args[0]==WRONG_COMMAND_MSG:
                        print(NOT_COMPELETED_MSG)
                        print(ex.args[0])
                        # for arg in ex.args:
                        #     print(arg)
                        continue
                raise ex
            
    except KeyboardInterrupt as ke:
        print(KI_MSG)
    except Exception as ex:
        print(ex)
    finally:
        detect_interrupt_process.terminate()
        print(EXIT_MSG)
        exit()