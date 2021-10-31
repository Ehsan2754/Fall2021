from xmlrpc.server import SimpleXMLRPCServer


class myQueue:
    def __init__(self):
        self.q = []

    def put(self, word: str):
        self.q.append(word)
        return True

    def pick(self):
        if len(self.q) > 0:
            return self.q[0]
        else:
            return NoneType

    def pop(self):
        if len(self.q) > 0:
            return self.q.pop(0)
        else:
            return NoneType
    def size(self):
        return len(self.q)


if __name__ == "__main__":
    ip = "localhost"
    port = 65000
    try:
        q = myQueue()
        with SimpleXMLRPCServer((ip, port), logRequests=False) as server:
            # Register functions
            server.register_instance(q)
            # Run the server's main loop
            server.serve_forever()
    except KeyboardInterrupt:
        print('KeyboardInterrupt')
    except Exception as e:
        print('!Error')
        print(e)
