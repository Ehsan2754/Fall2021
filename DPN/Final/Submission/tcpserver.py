from hash import calc_hash
import socket
import threading
import hashlib


def calc_hash(str_in: str):
    return hashlib.md5(str_in.encode('utf-8')).hexdigest()


ADDR = ("127.0.0.1", 50505)


def handle_client(client, addr):
    while True:
        msg_bytes = client.recv(2058)
        if not msg_bytes:
            client.close()
            clients.pop(addr)
            print('Client disconnected')
            break
        msg = msg_bytes.decode()
        client.send(str.encode(calc_hash(msg)))
        print('Message: ',msg)


clients = {}
if __name__ == "__main__":

    # Creating the TCP socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:       # Handling binding error
        s.bind(ADDR)  # Binding the socket to IP address and the preffered port
        print('Server is running on ', ADDR)
        s.listen(5)
        while True:
            client, address = s.accept()    # waiting fo client to connect again
            print('Client connected')
            clients[address] = threading.Thread(
                target=handle_client, args=(client, address)
            )
            clients[address].start()

    except socket.error as err:
        print('!ERROR: CAN NOT BIND TO ', ADDR)
        s.close()
        exit()
    except KeyboardInterrupt:
        print('Server is stopped')
    finally:
        s.close()
