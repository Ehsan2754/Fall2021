import socket
# CONSTANTS

OPERATIONS_CMD = '* / - + > < >= <='.split()
ARG_LEN = 3
QUIT_CMD = 'quit'
KI_CMD = 'KI' # KeyboardInterrupt command
EXIT_MSG = '>> Server is shutting down...'
READY_MSG = '#### UDP-SERVER IS WAITITNG FOR REQUEST ... ####'
REQ_MSG = '>> REQUEST RECEIVED FROM (IP={0},PORT={1}): ${2}'
TIMEOUT_MSG = '! SERVER LISTENING TIMEOUT AFTER {0}s.'
IP_ADDR = 'localhost'
PORT = 40047
BUFFER_SIZE = 1024
TIMEOUT = 59.9

# EXCEPTOPNS
class CALC_EX(Exception):
    pass
class EmptyInput(CALC_EX):
    msg = '\t! EMPTY INPUT'
class InvalidInput(CALC_EX):
    msg = '\t! INVALID INPUT'
class InvalidOperator(CALC_EX):
    msg = '\t! INVALID OPERATOR'
    def __init__(self,opt):
        self.opt = '\t' + opt
class InvalidArgs(CALC_EX):
    msg = '\t! INVALID ARGUMENTS'
    def __init__(self,arg):
        self.arg = '\t' + arg
class QuitCommandEx(Exception):
    msg = '\t! QUIT COMMAND RECEIVED'




'''
    evaluateOperatorAndArguments(arg):
    evaluates the supported operators and argumetns in a  string list of length 3 
'''
def evaluateOperatorAndArguments(arg):
    OPERATOR = arg[0]
    if OPERATOR in OPERATIONS_CMD: #checks if the operator is available on the list
        try:
            left_operand = ''
            right_operand = ''
            if ('.' in arg[1]) or ('.' in arg[2]): # checks if arguments contain point decclearing the argument type (float or int)
                left_operand = float(arg[1]) # tries to convert the inputs to float
                right_operand = float(arg[2])
            else:
                left_operand = int(arg[1])  # tries to convert the inputs to interger
                right_operand = int(arg[2])
            return str(eval('left_operand'+OPERATOR+'right_operand')) # returns the operation result
        except ValueError as ex:    # raises the ValueError in case of inappropriate argument
            raise InvalidArgs(arg[1]+' OR/AND '+arg[2])
        except ArithmeticError as ex:
            raise ex
            
    else:
        raise InvalidOperator(opt=OPERATOR) # raises invalid exception in case of failure

    

'''
    evaluateInput(cmd):
    evaluates the inputs in terms of length and adminstrative commands and returns the standard 3 member argument list
'''
def evaluateInput(cmd):  
    ARGS = cmd.split() # Split the input string for evaluation
    # print(ARGS)
    if len(ARGS)<ARG_LEN: # Check the length of the arguments comparting to the ARG_LEN constant
        if len(ARGS) == 0 or ARGS == None: #if the command is empty
            raise  EmptyInput
        if len(ARGS) == 1 : # check if the command is  a quit/KeyboardInterrupt
            if ARGS[0] == KI_CMD :
                raise KeyboardInterrupt      # raising KeyboardInterrupt excetpion
            if ARGS[0].lower() == QUIT_CMD :
                raise QuitCommandEx             # raising Quit exception
            else: 
                raise InvalidInput # in other cases the command is Invalid!
        else: 
            raise InvalidInput # in other cases the command is Invalid!
    if len(ARGS)==ARG_LEN: # if the length of input command matches the ARG_LEN constant
        return ARGS
    if len(ARGS)>ARG_LEN : # if the length of input command is more than ARG_LEN constant raise the InvalidInput excception
        raise InvalidInput()        
    
def respond (input):
    RES = ' >> SERVER RESULT : ' +str(
        evaluateOperatorAndArguments(
            evaluateInput(
                input)))
    print(RES)
    return RES
if __name__ == '__main__':
    try:
        UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM) # Creating the UDP socket
        UDPServerSocket.settimeout(TIMEOUT)
        UDPServerSocket.bind((IP_ADDR, PORT)) # Binding the socket to IP address and the preffered port
        print(READY_MSG)
        while True:
            BYTE_ADDRESS_PAIRS = UDPServerSocket.recvfrom(BUFFER_SIZE) #listening till receiving the datagram
            CMD = BYTE_ADDRESS_PAIRS[0].decode('utf-8')
            ADDR = BYTE_ADDRESS_PAIRS[1]
            print(REQ_MSG.format(ADDR[0],ADDR[1],CMD))
            try:
                RES = str.encode(respond(CMD))
                UDPServerSocket.sendto(RES,ADDR)
            except KeyboardInterrupt:
                UDPServerSocket.sendto(str.encode(KI_CMD),ADDR)
                print('! KEYBOARD INTERRUPT ')
                print(EXIT_MSG)
                break
            except QuitCommandEx as ex:
                UDPServerSocket.sendto(str.encode(ex.msg),ADDR)
                print(ex.msg)
                print(EXIT_MSG)
                break
            except EmptyInput as ex:
                UDPServerSocket.sendto(str.encode(ex.msg),ADDR)
                print(ex.msg)
            except InvalidInput as ex:
                UDPServerSocket.sendto(str.encode(ex.msg),ADDR)
                print(ex.msg)
            except InvalidOperator as ex:
                UDPServerSocket.sendto(str.encode(ex.msg+ex.opt),ADDR)
                print(ex.msg+ex.opt)
            except InvalidArgs as ex:
                UDPServerSocket.sendto(str.encode(ex.msg+ex.arg),ADDR)
                print(ex.msg+ex.arg)
            except ZeroDivisionError as ex:
                UDPServerSocket.sendto(str.encode('\t ! ' + str(ex).upper()),ADDR)
                print(ex)
            except ArithmeticError as ex:
                UDPServerSocket.sendto(str.encode('\t ! ' + str(ex).upper()),ADDR)
                print(ex)
            except Exception as ex:
                UDPServerSocket.sendto(str.encode('\t SERVER ERROR ' + str(ex).upper()),ADDR)
                print(ex)
        UDPServerSocket.close()
    except socket.timeout as ex:
        print(TIMEOUT_MSG.format(TIMEOUT))
        print(EXIT_MSG)
        UDPServerSocket.close()
