from DPN.Lab3.server import TIMEOUT
from _typeshed import Self
import socket
from enum import Enum
# CONSTANTS
PAYLOAD_SIZE = 1472 # maximum payload for ETHERNET frame using UDP header
TRIAL_NUM = 5
# TODO
# SUPPORT BINARY
# SUPPORT FILE PATH
# CHUNK DATA IN ETH FRAME
QUIT_CMD = 'quit'
KI_CMD = 'KI' # KeyboardInterrupt command
EXIT_MSG = 'User has quit.'
ENTRY_MSG = 'ENTER COMMAND :\n$'

IP_ADDR = 'localhost'
PORT = 40047
BUFFER_SIZE = 1518
TIMEOUT = 0.5
def send_command(bin_str,socket,buffer_size,timeout):
    try:
        BYTE2SEND = str.encode(bin_str)
        socket.settimeout(timeout)
        socket.sendto(BYTE2SEND, (IP_ADDR,PORT))
        RES=socket.recvfrom(buffer_size)[0].decode('utf-8')
        return RES
    except Exception as ex:
        raise ex

class InvalidInputType(Exception):
    def __init__(self):
        self.args = ('Invalid type argument. use the enum class INPUT_TYPE to pass the parameter')    
# Enum class defining the datagram type
class INPUT_TYPE(Enum):
    PATH='PATH'
    DATA='DATA'
class DATAGRAM_TYPE(Enum):
    DATA = 'D'
    START = 'S'
class EhsanChunker:
    # Exception for case of empty path or data

    '''
    EhsanChunker is a class which chunks your data ETHERNET frames and provides methods to send through
        UDP socket to your server
    @parm arg: your PATH to your file or <class bytes>  serializable object as following: 
        *  an iterable yielding integers in range(256)
        *  a text string encoded using the specified encoding
        *  any object implementing the buffer API.
        *  an integer
        default = None
    @parm type: specifies your command type which is enum of <class INPUT_TYPE> default = INPUT_TYPE.DATA
    @parm IP_ADDRESS: IPv4 of Server in string format default = 'localhost'
    @parm PORT: SERVER port default = 5000
    '''
    def __init__(self,arg=None,type = INPUT_TYPE.DATA ,IP_ADDRESS='localhost' ,PORT=5000):
        self.IP_ADDR = IP_ADDRESS
        self.PORT = PORT
        self.datagrams  = []
        if type == INPUT_TYPE.DATA:
            try:
                self.BYTES2SEND = bytes(arg)
                self.EXTENTION = 'bin'
            except Exception as ex:
                raise ex
        elif type == INPUT_TYPE.PATH:
            try:
                file = open(arg, "rb")
                self.BYTES2SEND = file.read()
                self.EXTENTION = file.name.split('.')[-1]            
            except Exception as ex:
                raise ex
        else:
            raise InvalidInputType
        self.PACKET_LEN = len(self.BYTES2SEND)
        for i in range (0,self.PACKET_LEN//PAYLOAD_SIZE):
            self.datagrams.append(self.BYTES2SEND[i*PAYLOAD_SIZE:(i+1)*PAYLOAD_SIZE])
        if (self.PACKET_LEN%PAYLOAD_SIZE) > 0:   
            self.datagrams.append(self.BYTES2SEND[self.PACKET_LEN//PAYLOAD_SIZE*self.PAYLOAD_SIZE:])
        self.datagrams = [T for T in enumerate(self.datagrams)]
    
    def send_pkt(self,socket,timeout):
        for _ in range(5):
            try:
                pass
                # start pkt
            except socket.timeout:
                continue

        while(len(self.datagrams)):
            for _ in range(5):
                # data packs
                pass
        
        for _ in range(5):
            try:
                pass
                # end pkt
            except socket.timeout:
                continue
        


            




if __name__ == '__main__':
    try:
        UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM) # Creating UDP-Socket
        cmd = ''         # initial user command variable
        while True:      # infinite loop
            cmd = input(ENTRY_MSG).lower() # getting user input command and converting all to lowercase letters
            if cmd.lower() == QUIT_CMD:    # check if user entered QUIT command, break the loop
                send_command(QUIT_CMD,UDPClientSocket,IP_ADDR,PORT,BUFFER_SIZE) # send QUIT command to server
                break
            print(send_command(cmd,UDPClientSocket,IP_ADDR,PORT,BUFFER_SIZE)) # send the command to UDP-server and get the respose
        UDPClientSocket.close()
        print(EXIT_MSG)  # print EXIT message in case of manual quit command
    except KeyboardInterrupt:
        send_command(KI_CMD,UDPClientSocket,IP_ADDR,PORT,BUFFER_SIZE) # send KeyboardInterrupt command to server
        UDPClientSocket.close()
        print(EXIT_MSG) # print EXIT message in case of KeyboardInterrupt 
        
