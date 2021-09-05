
import socket, sys
from multiprocessing import Pipe, Process
from threading import Thread
from _thread import *
import random

# constants
BAD_INPUT='''Usage example: python ./server.py <port>'''
BINDING_ERR_MSG='''Error while binding to the specified port'''
SERVER_START_MSG='''Starting the server on {0}:{1}'''
LISTEN_MSG='''Waiting for a connection'''
KI_MSG='''KeyboardInterrupt'''
FULLSERVER_MSG='''The server is full'''
CLIENT_CONNECTED_MSG='''Client connected'''
WELCOME_MSG = '''Welcome to the number guessing game!\nEnter the range:'''
NUM_ATTEMPT_MSG = '''You have {0} attempts'''
WIN_MSG='''You win!'''
LOSE_MSG='''You lose'''
GTR_MSG='''Greater'''
LSS_MSG='''Less'''
IP_ADDR='127.0.0.1'
port=-1
TIMEOUT=5.0
MAX_CLIENTS=2
MIN_PORT=1000
MAX_PORT=23000
BUFFERSIZE=2048
new_port=random.randint(MIN_PORT,MAX_PORT)
clients={}

class Exit(Exception):
    pass

def GAME_LOGIC(new_port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # Creating the TCP socket
    s.settimeout(TIMEOUT)   #setting the timeout 
    try :       # Handling binding error
        s.bind((IP_ADDR, new_port)) # Binding the socket to IP address and the preffered port
    except socket.error as err: #getting the Binging Error
        print(BINDING_ERR_MSG)
        s.close()
    try:
        s.listen(MAX_CLIENTS)                     
        client, address = s.accept()    # waiting fo client to connect again
        client.send(str.encode(WELCOME_MSG)) # send the message to the client
        RES=client.recv(BUFFERSIZE)
        if not RES: raise Exit 
        a,b = map(int,RES.decode().split()) # getting boundaries 

        NUM = random.randint(a,b) # generate a random integer within a,b (including a,b)
        for i in range(5,0,-1):
            client.send(str.encode(NUM_ATTEMPT_MSG.format(i)))
            RES=client.recv(BUFFERSIZE)
            if not RES: raise Exit
            reply=int(RES.decode())
            if reply == NUM:    #the winning case of the client
                client.send(str.encode(WIN_MSG))
                break
            else:
                if i == 1:      # the lose case
                    client.send(str.encode(LOSE_MSG))
                    break
                elif reply>NUM:
                    client.send(str.encode(LSS_MSG))
                elif reply<NUM:
                    client.send(str.encode(GTR_MSG))
    except Exit:
        pass
    except Exception as ex:
        raise ex
    finally:
        client.close()
        s.close()
        clients.pop(new_port)



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
    if (len(args)!=1) or (not args[0].isnumeric()): # Handles bad input
        print(BAD_INPUT)
        exit()
    port = int(args[0]) # Setting the PORT
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # Creating the TCP socket
    try :       # Handling binding error
        s.bind((IP_ADDR, port)) # Binding the socket to IP address and the preffered port
        print(SERVER_START_MSG.format(IP_ADDR,port))
    except socket.error as err:
        print(BINDING_ERR_MSG)
        exit()
    try:
        # Crate a Pipe for IPC
        main_conn, detect_conn = Pipe()
        # Create a thread in main process to listen on connection
        listen_for_interrupt_thread = Thread(
            target=listen_for_interrupt, args=(main_conn, s), daemon=True)
        listen_for_interrupt_thread.start()
        # Create a separate process to detect the KeyboardInterrupt
        detect_interrupt_process = Process(
            target=detect_interrupt, args=(detect_conn,))
        detect_interrupt_process.start()

        s.listen(5)
        print(LISTEN_MSG)
        while True:
            client, address = s.accept()
            if len(clients) == MAX_CLIENTS:    # checks the number of served clients.
                print(FULLSERVER_MSG)
                client.send(str.encode(FULLSERVER_MSG)) # sends server full message
                client.close()
                continue
            while new_port in clients.keys(): # generate a new port which is not in not used by other clients 
                new_port = random.randint(MIN_PORT,MAX_PORT)
            clients[new_port]=client #add new client and the dictionary
            start_new_thread(GAME_LOGIC, (new_port, )) # start the game theread
            client.send(str.encode(str(new_port)))  # sending new port number to the client
            print(CLIENT_CONNECTED_MSG)
            client.close()
        
    except KeyboardInterrupt as ex:
        print(KI_MSG)
        exit()
   
    finally:
        detect_interrupt_process.terminate()
        s.close()
        
