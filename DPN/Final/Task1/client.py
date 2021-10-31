from xmlrpc.client import ServerProxy

if __name__ == "__main__":
    ip = "localhost"
    port = 65000
    while True:
        try:
            proxy = ServerProxy("http://{0}:{1}".format(ip, port))
            cmd = input('Enter command: ')
            cmd = cmd.split()
            if len(cmd) == 0:
                continue
            if cmd[0] == 'size':
                res = proxy.size()
                print(res)
            elif cmd[0] == 'put':
                if len(cmd) < 2:
                    print('Bad Argument')
                    continue
                res = proxy.put(cmd[1])
            elif cmd[0] == 'pick':
                res = proxy.pick()
                print(res)
            elif cmd[0] == 'pop':
                res = proxy.pop()
                print(res)
            else:
                print('\nInvalid Command!')
                continue


        except KeyboardInterrupt:
            print('\nClosing')
            break
        except Exception as e:
            print('\n!Error')
            print(e)
            break
