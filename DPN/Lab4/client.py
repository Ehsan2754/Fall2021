
from os import close
import socket,sys
from multiprocessing import Pipe, Process
from threading import Thread
BAD_INPUT='''Usage example: python ./client.py <address> <port>'''
host='127.0.0.1'
port=6000
TIMEOUT=5.0
BUFFERSIZE=2048 
FULLSERVER_MSG='''The server is full'''
SERVER_NA_MSG='''Server is unavailable'''
CNNLOSS_MSG='''Connection lost'''
RANGE_MSG='''Enter the range:'''
WIN_MSG='''You win!'''
LOSE_MSG='''You lose'''

def detect_interrupt(conn):
    try:
        while True:
            pass
    except KeyboardInterrupt:
        conn.send(True)
        conn.close()

def listen_for_interrupt(conn, sock):
    conn.recv()
    sock.close()



if __name__ == '__main__':
    args = sys.argv[1:]  # getting args
    # checking length of arguments
    ARGLEN_FLG = len(args)==2
    if not ARGLEN_FLG:
        print(BAD_INPUT)
        exit()
    #checing if the ip addr is a valid IPv4
    IP_FLG=len(args[0].split('.'))==4
    # checing it the address is valid
    for block in args[0].split('.'):
        IP_FLG = IP_FLG and block.isnumeric()
    PORT_FLG=args[1].isnumeric()
    if not(IP_FLG and PORT_FLG): # Handles bad input
        print(BAD_INPUT)
        exit()
    
    host = args[0]
    port = int(args[1])
    
    ClientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #Creating TCP socket
    ClientSocket.settimeout(TIMEOUT)
    try:
        # Crate a Pipe for IPC
        main_conn, detect_conn = Pipe()
        # Create a thread in main process to listen on connection
        listen_for_interrupt_thread = Thread(
            target=listen_for_interrupt, args=(main_conn, ClientSocket), daemon=True)
        listen_for_interrupt_thread.start()
        # Create a separate process to detect the KeyboardInterrupt
        detect_interrupt_process = Process(
            target=detect_interrupt, args=(detect_conn,))
        detect_interrupt_process.start()
        ClientSocket.connect((host, port)) # REQUEST FOR  THE PORT NUMBER ON SERVER
        REPLY=ClientSocket.recv(BUFFERSIZE).decode()
        if(REPLY==FULLSERVER_MSG):  # checks if server accepted the communication
            print(FULLSERVER_MSG)
            exit()
        port=int(REPLY) # gets the port number
        ClientSocket.close()
        ClientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #Creating TCP socket
        ClientSocket.connect((host,port)) # Connects to the new port
        WELCOM=ClientSocket.recv(BUFFERSIZE).decode()
        print(WELCOM)
        t = input().split()

        while True:
            if(len(t)==2) and (
                t[0].isnumeric() and t[1].isnumeric()) and (
                    int(t[0])<int(t[1])
                ):
                break   #breaks in case of true input
            t=input(RANGE_MSG).split()
        t = t[0]+' '+t[1]
        ClientSocket.send(str.encode(t))
        SERVER_RES = ClientSocket.recv(BUFFERSIZE).decode()
        while True:
            print(SERVER_RES)
            t=input()
            if not t.isnumeric():
                continue
            ClientSocket.send(t.encode())
            SERVER_RES=ClientSocket.recv(BUFFERSIZE).decode()
            print(SERVER_RES)
            if(SERVER_RES == WIN_MSG)or(SERVER_RES== LOSE_MSG):
                break
            SERVER_RES=ClientSocket.recv(BUFFERSIZE).decode()
        exit()      
    except socket.timeout:  #if timeout happens it shows the communication is lost
        print(CNNLOSS_MSG)
        exit()
    except ConnectionRefusedError as E: # HANDLES UNAVAILABLE SERVER SITUATION
        print(SERVER_NA_MSG) 
        exit()
    except KeyboardInterrupt as KI:
        exit()
    except Exception as ex:
        print(ex)
    finally:
        detect_interrupt_process.terminate()
        ClientSocket.close()
        exit()