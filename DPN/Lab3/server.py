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
BUFFER_SIZE = 1518
TIMEOUT = 59.9
PATH = './'
# EXCEPTOPNS
import random

class QuitCommandEx(Exception):
    msg = '\t! QUIT COMMAND RECEIVED'

class DATAGRAM_TYPE:
    DATA = 'd'
    START = 's'
    ACK = 'a'
def genCMD(CMD_TYPE,SEQ_NO,arg1=None,arg2=None,arg3=None,data=None):
    res =  f'{CMD_TYPE}|{SEQ_NO}'
    if arg1 : res+=f'|{arg1}'
    if arg2 : res +=f'|{arg2}'
    if arg3 : res +=f'|{arg3}'
    res = str.encode(res+'|')+data if data else str.encode(res)
    return res
if __name__ == '__main__':
    try:
        UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM) # Creating the UDP socket
        UDPServerSocket.settimeout(TIMEOUT)
        UDPServerSocket.bind((IP_ADDR, PORT)) # Binding the socket to IP address and the preffered port
        print(READY_MSG)
        while True:
            BYTE_ADDRESS_PAIRS = UDPServerSocket.recvfrom(BUFFER_SIZE) #listening till receiving the datagram
            CMD = BYTE_ADDRESS_PAIRS[0].decode().split('|')
            REQ_TYPE = CMD[0]
            REQ_SEQNO = CMD[1]
            REQ_EXT = CMD[2]
            REQ_SIZE = CMD[3]
            ADDR = BYTE_ADDRESS_PAIRS[1]
            print(REQ_MSG.format(ADDR[0],ADDR[1],BYTE_ADDRESS_PAIRS[0].decode()))
            try:
                UDPServerSocket.sendto(genCMD(DATAGRAM_TYPE.ACK,int(REQ_SEQNO)+1,BUFFER_SIZE),ADDR)
                
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
            res=str.encode('')
            while len(res)<int(REQ_SIZE):
                BYTE_ADDRESS_PAIRS = UDPServerSocket.recvfrom(BUFFER_SIZE) #listening till receiving the datagram
                socket.setdefaulttimeout(2.5) # checks if the client gave up on sending
                CMD = BYTE_ADDRESS_PAIRS[0].decode().split('|')
                REQ_TYPE = CMD[0]
                REQ_SEQNO_new = CMD[1]
                if(int(REQ_SEQNO_new)<=int(REQ_SEQNO)):#discarding replicated packets
                    continue
                else:
                    REQ_SEQNO = REQ_SEQNO_new
                DATA = CMD[2]
                res+=str.encode(DATA)
                ADDR = BYTE_ADDRESS_PAIRS[1]
                print('\t',BYTE_ADDRESS_PAIRS[0].decode())
                try:
                    UDPServerSocket.sendto(genCMD(DATAGRAM_TYPE.ACK,int(REQ_SEQNO)+1),ADDR)
                except socket.timeout: # listens for new client
                    break
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
            print(res.decode())
            t = PATH+str(random.randint(0,10000000000))+'.'+REQ_EXT
            open(t, 'a').close()
            f = open(t, 'wb')
            f.write(res)
            f.close()
            

            # except Exception as ex:
            #     UDPServerSocket.sendto(str.encode('\t SERVER ERROR ' + str(ex).upper()),ADDR)
            #     print(ex)
        UDPServerSocket.close()
    except socket.timeout as ex:
        print(TIMEOUT_MSG.format(TIMEOUT))
        print(EXIT_MSG)
        UDPServerSocket.close()
