# from functools import cmp_to_key
# from DPN.Lab3.server import RES, TIMEOUT
# from _typeshed import Self
# from DPN.Lab3.server import InvalidInput
import socket
from enum import Enum
# CONSTANTS
PAYLOAD_SIZE_t = 1472 # maximum payload for ETHERNET frame using UDP header
RESERVE = 7 # D | XXXX<seq.num> | <DATA>
TRIAL_NUM = 5
# TODO
# SUPPORT BINARY
# SUPPORT FILE PATH
# CHUNK DATA IN ETH FRAME
QUIT_CMD = 'quit'
KI_CMD = 'KI' # KeyboardInterrupt command
EXIT_MSG = 'User has quit.'
ENTRY_MSG = '''ENTER COMMAND:\nP\n'---->\tYOU WANT TO SEND FILE BY ENTERING THE PATH\nD\n'---->\tYOU WANT TO SEND A STRING TO THE SERVER WHICH WILL BE SAVED IN BINARY(.bin) FORMAT\n$'''

IP_ADDR = 'localhost'
PORT = 40047
BUFFER_SIZE = 1518
TIMEOUT = 0.5
seq_no = 0

def send_command(bin_str,socket,buffer_size,timeout):
    try:
        BYTE2SEND = (bin_str)
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
class INPUT_TYPE:
    PATH='d'
    DATA='p'
class DATAGRAM_TYPE:
    DATA = 'd'
    START = 's'
    ACK = 'a'
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
    def __init__(self,arg=None,type = INPUT_TYPE.DATA):
        self.datagrams  = []
        if type == INPUT_TYPE.DATA:
            try:
                self.BYTES2SEND = str.encode(arg)
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
        self.SIZE = len(self.BYTES2SEND)    

    def genCMD(self,CMD_TYPE,SEQ_NO,arg1=None,arg2=None,arg3=None,data=None):
        res =  f'{CMD_TYPE}|{SEQ_NO}'
        if arg1 : res+=f'|{arg1}'
        if arg2 : res +=f'|{arg2}'
        if arg3 : res +=f'|{arg3}'
        print(data)
        res = (str.encode(res+'|')+data) if data else str.encode(res)
        return res
    
    # to-do
    # interpret incomming data.
    def interpretCMD(self,cmd):
        return cmd.split('|')

    def chuck(self,chunkSize = PAYLOAD_SIZE_t): #divides packet into buffer size managed data
        self.PACKET_LEN = len(self.BYTES2SEND)
        for i in range (0,self.PACKET_LEN//chunkSize):
            self.datagrams.append(self.BYTES2SEND[i*chunkSize:(i+1)*chunkSize])
        if (self.PACKET_LEN%chunkSize) > 0:   
            self.datagrams.append(self.BYTES2SEND[self.PACKET_LEN//chunkSize*chunkSize:])
        self.datagrams = [T for T in enumerate(self.datagrams,1)] # labling packets by numbers from 1.


    def send_pkt(self,socket,timeout=TIMEOUT):
        server_resp = []
        # ---- starting communication
        for i in range(5):
            try: # try to start communication with server
                # start pkt
                server_resp = self.interpretCMD(
                    send_command(
                    self.genCMD(DATAGRAM_TYPE.START,seq_no,self.EXTENTION,self.SIZE),
                    socket,
                    BUFFER_SIZE,
                    timeout
                )
                )
                print(
                    'Client\t>>\tServer: REQUEST :\t','TYPE=',DATAGRAM_TYPE.START,
                    '.:.\t','SEQ No.=',seq_no,
                    '.:.\t','EXT.=',self.EXTENTION,
                    '.:.\t','FILE-SIZE=',self.SIZE
                )
                break # breaks the loop if no timeout or other exception happened
            # except socket.timeout as ex:
            except Exception as ex:
                print(ex)
                if i == 4: # raises the timeout exception if the timeout happened 5 times(i=4)
                    raise ex
                else:      # if its less than five times trying it retries sending the command
                    continue
        print(server_resp)
        RESP_TYPE = server_resp[0]
        RESP_SEQNO = server_resp[1]
        RESP_BUFFERSIZE = server_resp[2] 
        self.chuck(PAYLOAD_SIZE_t-RESERVE)
        print(self.datagrams)
        print(
            'Client\t<<\tServer: RESPOND :\t','TYPE=',RESP_TYPE,
            '.:.\t','SEQ No.=',RESP_SEQNO,
            '.:.\t','BUFFER SIZE=',RESP_BUFFERSIZE
        )
        while(len(self.datagrams)):
            # ---- starting communication
            data=self.datagrams.pop(0)
            for i in range(5):
                try: # try to send data chunks to server
                    server_resp = self.interpretCMD(
                        send_command(
                        self.genCMD(CMD_TYPE=INPUT_TYPE.DATA,SEQ_NO=RESP_SEQNO,data=data[1]),
                        socket,
                        BUFFER_SIZE,
                        timeout
                    ))
                    print(
                        'Client\t>>\tServer: REQUEST :\t','TYPE=',DATAGRAM_TYPE.DATA,
                        '.:.\t','SEQ No.=',RESP_SEQNO,
                        '.:.\tDATA=\n',data
                    )
                    RESP_TYPE = server_resp[0]
                    RESP_SEQNO = server_resp[1]
                    print(
                         'Client\t<<\tServer: RESPOND :\t','TYPE=',RESP_TYPE,
                         '.:.\t','SEQ No.=',RESP_SEQNO,
                         '.:.\t','SIZE=',RESP_BUFFERSIZE
                    )
                    break # breaks the loop if no timeout or other exception happened
                # except socket.timeout as ex:
                except Exception as ex:
                    if i == 4: # raises the timeout exception if the timeout happened 5 times(i=4)
                        raise ex
                    else:      # if its less than five times trying it retries sending the command
                        continue


if __name__ == '__main__':
    try:
        UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM) # Creating UDP-Socket
        cmd = ''         # initial user command variable
        while True:      # infinite loop
            cmd = input(ENTRY_MSG).lower() # getting user input command and converting all to lowercase letters
            if cmd.lower() == QUIT_CMD:    # check if user entered QUIT command, break the loop
                # send_command(QUIT_CMD,UDPClientSocket,IP_ADDR,PORT,BUFFER_SIZE) # send QUIT command to server
                break
            dtype = ''
            if cmd == 'd':
                dtype = INPUT_TYPE.DATA 
            elif cmd == 'p':
                dtype = INPUT_TYPE.PATH 
            else:
                raise InvalidInputType
            arg = input('Enter the <PATH> OR the STRING you want to send.')
            # print(send_command(cmd,UDPClientSocket,IP_ADDR,PORT,BUFFER_SIZE)) # send the command to UDP-server and get the respose
            
            chunks = EhsanChunker(arg = arg,
            type=dtype)
            chunks.send_pkt(UDPClientSocket,TIMEOUT)
        UDPClientSocket.close()
        print(EXIT_MSG)  # print EXIT message in case of manual quit command
    except KeyboardInterrupt:
        # send_command(KI_CMD,UDPClientSocket,IP_ADDR,PORT,BUFFER_SIZE) # send KeyboardInterrupt command to server
        UDPClientSocket.close()
        print(EXIT_MSG) # print EXIT message in case of KeyboardInterrupt 
        
