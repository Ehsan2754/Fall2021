import socket
# CONSTANTS
QUIT_CMD = 'quit'
KI_CMD = 'KI' # KeyboardInterrupt command
EXIT_MSG = 'User has quit.'
ENTRY_MSG = 'ENTER COMMAND :\n$'

IP_ADDR = 'localhost'
PORT = 40047
BUFFER_SIZE = 1024

def send_command(cmd,socket,ip_addr,port,buffer_size):
    BYTE2SEND = str.encode(cmd)
    socket.sendto(BYTE2SEND, (IP_ADDR,PORT))
    RES=socket.recvfrom(buffer_size)[0].decode('utf-8')
    return RES

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
        
