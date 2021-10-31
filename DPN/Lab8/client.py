from mylib import *
import logging
import xmlrpc.client
from logging import debug
logging.basicConfig(encoding='utf-8', level=logging.DEBUG)

if __name__ == '__main__':
    try:
        nodes = parseConf(CONFIG_PATH)
        proxy = None
        input_ = input('>')
        while(input_ != 'quit'):
            cmd = input_.split()
            if len(cmd) == 1:
                if cmd[0] == 'getleader':
                    if proxy:
                        try:
                            # TODO: GET_LEADER CONNECTED NODE BY RPC-SERVER
                            LEADER_ID, LEADER_ADDR_PORT_PAIR = proxy.GetLeader()
                            print(CLIENT_MSGS.LEADER_ADDR.format(LEADER_ID,
                                                                    LEADER_ADDR_PORT_PAIR[0],
                                                                    LEADER_ADDR_PORT_PAIR[1]))
                        except ConnectionRefusedError as e:
                            proxy = None
                            print(CLIENT_MSGS.PROXY_NA.format(
                                TARGET_ADDR, TRAGET_PORT))
                    else:
                        print('!First connect to node!')
            elif len(cmd) == 2:
                if cmd[0] == 'suspend':
                    if cmd[1].isnumeric():
                        period = int(cmd[1])
                        if proxy:
                            try:
                            # TODO: SUSPEND CONNECTED NODE BY RPC-SERVER
                                proxy.Suspend(period)

                            except ConnectionRefusedError as e:
                                proxy = None
                                print(CLIENT_MSGS.PROXY_NA.format(
                                    TARGET_ADDR, TRAGET_PORT))

                        else:
                            print('!First connect to node!')
                    else:
                        raise BadArgumentException(
                            '!NODE-ID NOT IN CONFIGURATION FILE')
            elif len(cmd) == 3:
                if cmd[0] == 'connect':
                    if cmd[2].isnumeric():
                        TARGET_ADDR = cmd[1]
                        TRAGET_PORT = cmd[2]
                        proxy = xmlrpc.client.ServerProxy(
                            PROXY_URI.format(TARGET_ADDR, TRAGET_PORT))



            else:
                raise BadArgumentException("!INVALID ENTRY FORMAT.")
            input_ = input('>')
    except KeyboardInterrupt:
        print('KeyboardInterrupt')
    except BadArgumentException as e:
        print('INVALID ARGUMENT.\t>', e.args[0])
    except Exception as e:
        print(e)
    finally:
        print(CLIENT_MSGS.EXIT)
