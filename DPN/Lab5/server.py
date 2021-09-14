from enum import Flag
import sys, os
from multiprocessing import Pipe, Process
from threading import Thread
from xmlrpc.server import SimpleXMLRPCServer
# from xmlrpc.server import SimpleXMLRPCRequestHandler
import xmlrpc

ip = "127.0.0.1"
port = 6000
PATH = os.path.dirname(os.path.realpath(__file__)) + "/SERVER_FILES"
BAD_ARG_MSG = """Usage example: python ./server.py <address> <port>"""
ENTER_MSG = "\nEnter the command:"
KI_MSG = "KeyboardInterrupt"
EXIT_MSG = "Server is stopping"
COMELETED_MSG = "Completed"
NOT_COMPELETED_MSG = "Not completed"
WRONG_COMMAND_MSG = "Wrong command"
NO_FILE_MSG = "No such file: {0}"
FILE_SEND = "File send: {0}"
EXISTING_FILE_MSG = "File already exists"
WRONG_EXPR_MSG = "Wrong expression"
DIVISION_BY_ZERO_MSG = "Division by zero"
NOTSAVED_MSG = "{0} not saved"
SAVED_MSG = "{0} saved"
NOTDELETED_MSG = "{0} not deleted"
DELETED_MSG = "{0} deleted"
EXPRESSION_DONE_MSG = "{0} -- done"
EXPRESSION_NOT_DONE_MSG = "{0} -- not done"
QUIT_CMD = ("quit",)
SEND_CMD = ("send", "<filename>")
LIST_CMD = ("list",)
DELETE_CMD = ("delete", "<filename>")
GET_CMD = ("get", "<filename>", "<new filename>")
CALC_CMD = ("calc", "<expression>")
EXPRESSION = ("OPERATOR", "LEFT_OPERAND", "RIGHT_OPERAND")
CMD_DICT = {
    QUIT_CMD[0]: QUIT_CMD[1:],
    SEND_CMD[0]: SEND_CMD[1:],
    LIST_CMD[0]: LIST_CMD[1:],
    DELETE_CMD[0]: DELETE_CMD[1:],
    GET_CMD[0]: GET_CMD[1:],
    CALC_CMD[0]: EXPRESSION,
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
    return input[0], int(input[1])

def send_file(filename, data):
    try:
        output_file_path = PATH + "/" + filename
        if os.path.isfile(output_file_path):
            print(NOTSAVED_MSG.format(filename))
            return False
        with open(output_file_path, "wb") as handle:
            handle.write(data.data)
            print(SAVED_MSG.format(filename))
            return True
    except Exception as ex:
        raise ex

def list_files():
    try:
        return os.listdir(PATH)
    except:
        raise ex

def delete_file(filename):
    try:
        output_file_path = PATH + "/" + filename
        if not os.path.isfile(output_file_path):
            print(NOTDELETED_MSG.format(filename))
            return False
        os.remove(output_file_path)
        print(DELETED_MSG.format(filename))
        return True
    except Exception as ex:
        raise ex

def get_file(filename):
    try:
        output_file_path = PATH + "/" + filename
        if not os.path.isfile(output_file_path):
            print(NO_FILE_MSG.format(filename))
            return False
        with open(output_file_path, "rb") as handle:
            data = handle.read()
            print(FILE_SEND.format(filename))
            return data
    except Exception as ex:
        raise ex

def calculate(op,Lop,Rop):
    OPERATIONS_CMD = '* / - + > < >= <='.split()
    OPERATOR = op
    if OPERATOR in OPERATIONS_CMD: #checks if the operator is available on the list
        try:
            Flag=True
            tmpL=Lop.replace('.','')
            tmpR=Rop.replace('.','')
            if not(tmpL.isnumeric() and tmpR.isnumeric()):
                return (False,"Invalid Operand",Lop+" AND/OR "+Rop)
            left_operand = ''
            right_operand = ''
            if ('.' in Lop) or ('.' in Rop): # checks if arguments contain point decclearing the argument type (float or int)
                left_operand = float(Lop) # tries to convert the inputs to float
                right_operand = float(Rop)
            else:
                left_operand = int(Lop)  # tries to convert the inputs to interger
                right_operand = int(Rop)
            return (True,str(eval('left_operand'+OPERATOR+'right_operand'))) # returns the operation result
        except ZeroDivisionError as ex:
            Flag=False
            print(EXPRESSION_NOT_DONE_MSG.format(op+' '+Lop+' '+Rop))
            return (False, DIVISION_BY_ZERO_MSG)
        except ValueError as ex:    # handles the ValueError in case of inappropriate argument
            Flag=False
            print(EXPRESSION_NOT_DONE_MSG.format(op+' '+Lop+' '+Rop))
            return (False,WRONG_EXPR_MSG,"Value Error")
        except ArithmeticError as ex:
            Flag=False
            print(EXPRESSION_NOT_DONE_MSG.format(op+' '+Lop+' '+Rop))
            return (False,WRONG_EXPR_MSG,"Arithmetic Error")    
        finally:
            if(Flag):
                print(EXPRESSION_DONE_MSG.format(op+' '+Lop+' '+Rop))
    else:
        print(EXPRESSION_NOT_DONE_MSG.format(op+' '+Lop+' '+Rop))
        return (False,WRONG_EXPR_MSG,"Invalid Operator") # raises invalid exception in case of failure



if __name__ == "__main__":
    try:
        # HANDLE KI PARALLEL
        # Crate a Pipe for IPC
        main_conn, detect_conn = Pipe()
        # Create a thread in main process to listen on connection
        listen_for_interrupt_thread = Thread(
            target=listen_for_interrupt, args=(main_conn,), daemon=True
        )
        listen_for_interrupt_thread.start()
        # Create a separate process to detect the KeyboardInterrupt
        detect_interrupt_process = Process(target=detect_interrupt, args=(detect_conn,))
        detect_interrupt_process.start()
        # GETTING IP and PORT
        ip, port = eval_args(sys.argv[1:])  # getting and evaluating user input args
        # CREATING SERVER FILE DIRECTORY 
        if not os.path.isdir(PATH):
            os.mkdir(PATH)
        # Restrict to a particular path.
        # class RequestHandler(SimpleXMLRPCRequestHandler):
        #     rpc_paths = ('/RPC2',)
        # Create server
        with SimpleXMLRPCServer((ip, port),logRequests=False) as server:
            # Register functions
            server.register_function(send_file,SEND_CMD[0])
            server.register_function(list_files,LIST_CMD[0])
            server.register_function(delete_file,DELETE_CMD[0])
            server.register_function(get_file,GET_CMD[0])
            server.register_function(calculate,CALC_CMD[0])
            # Run the server's main loop
            server.serve_forever()

    except KeyboardInterrupt as ke:
        print(KI_MSG)
    except Exception as ex:
        print(ex)
    finally:
        detect_interrupt_process.terminate()
        print(EXIT_MSG)
        exit()
