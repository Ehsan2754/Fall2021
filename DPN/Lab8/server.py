# configuring my log env
from os import close
from time import sleep
import xmlrpc.client
import xmlrpc.server
import threading
import sys
from math import ceil
from mylib import *
from logging import debug
# logging.basicConfig(level=logging.DEBUG)
# other imports


class NodeTimer(threading.Thread):
    def __init__(self, name, time_interval, timeUp_set):
        self.time_interval = time_interval
        self.dead = False
        self.timeUp_set = timeUp_set
        super().__init__(name=name, daemon=True)

    def kill(self):
        self.dead = True

    def run(self):
        sleep(self.time_interval)
        if not self.dead:
            self.timeUp_set()


class Node():

    def __election_routine(self, node_id, votes):
        res = (False, -1)
        try:
            proxy = xmlrpc.client.ServerProxy(
                PROXY_URI.format(*self.NODES.get(node_id, (None, None))))
            res = proxy.RequestVote(self.term_number, self.id)
            self.reset_timer()  # reset timer after each message
        except ConnectionRefusedError as e:
            res = (False, -1)
        finally:
            votes[node_id] = res

    def __heartbeat_routine(self, node_id, ack):
        res = (False, -1)
        try:
            proxy = xmlrpc.client.ServerProxy(
                PROXY_URI.format(*self.NODES.get(node_id, (None, None))))
            res = proxy.AppendEntries(self.term_number, self.id)
            ack[node_id] = res
            self.reset_timer()  # reseting timer after receiving heart-beat
        except ConnectionRefusedError as e:
            res = (False, -1)
        finally:
            ack[node_id] = res

    def __state_manager_routine(self):
        while True:
            # Catches the state update event
            self.state_update_event.wait()
            # Clears the event to wait for new event.
            self.state_update_event.clear()
            # TODO : Every time Follower receives a message from the Leader, it resets the timer.
            if self.state == NODE_STATE.Follower:
                print(SERVER_MSGS.FOLLOWER_STATUS.format(self.term_number))
                while True:
                    if self.timer_event.is_set():
                        print(SERVER_MSGS.DEAD_LEADER)
                        self.timer_event.clear()
                        self._set_state(NODE_STATE.Candidate)
                        break
                    if self.state_update_event.is_set():
                        break
            elif self.state == NODE_STATE.Candidate:
                # TODO : if node became a candidate it increments its term number and resets its timer
                self.term_number += 1
                print(SERVER_MSGS.CANDIDATE_STATUS.format(self.term_number))
                votes = {}
                voters = list(self.NODES.keys())
                # voting for itself
                if voters.count(self.id) > 0:
                    voters.remove(self.id)
                self.vote_event.set()
                votes[self.id] = [True, self.term_number]
                # TODO: requests votes from all other nodes.
                threads = [threading.Thread(
                    target=self.__election_routine,
                    args=(voter_id, votes)) for voter_id in voters]
                for thread in threads:
                    thread.start()
                for thread in threads:
                    thread.join()
                print(SERVER_MSGS.VOTE_RECEIVED)
                num_votes = 0
                for vote in votes.values():
                    if vote[0]:
                        num_votes += 1
                    # If the Candidate receives the message (any message) with the term number greater than its own,
                    # it stops the election and becomes a Follower. Also, it should update its term number with received
                    # term in this case.
                    if (not vote[0]) and vote[1] > self.term_number:
                        self.term_number = vote[1]
                        # re-initiating the timer if the election fails
                        self.initiate_timer()
                        self._set_state(NODE_STATE.Follower)
                        continue
                # Checks if received an vote-request with bigger term number, then new state is a follower
                if self.state_update_event.is_set():
                    # re-initiating the timer if the election fails
                    self.initiate_timer()
                    continue
                # If it has the majority of votes before the timer is up, the Candidate becomes a Leader
                if (num_votes >= self.majority) and (not self.timer_event.is_set()):
                    self._set_state(NODE_STATE.Leader)
                else:
                    # re-initiating the timer if the election fails
                    self.initiate_timer()
                    self._set_state(NODE_STATE.Follower)
            elif self.state == NODE_STATE.Leader:
                print(SERVER_MSGS.LEADER_STATUS.format(self.term_number))
                while not self.state_update_event.is_set():
                    # TODO: Every 50 milliseconds sends an AppendEntries request to all other servers. This is the heartbeat message.
                    # If the Leader receives a heartbeat message from another Leader with the term number greater than its own,
                    # it becomes a Follower (and also sets its term number to the new leader's one).
                    sleep(50/1000)

                    followers = list(self.NODES.keys())
                    if followers.count(self.id) > 0:
                        followers.remove(self.id)
                    # TODO: send HEARTBEAT to the followers.
                    pulses = {}
                    threads = [threading.Thread(
                        target=self.__heartbeat_routine,
                        args=(follower_id, pulses)) for follower_id in followers]
                    for thread in threads:
                        thread.start()
                    for thread in threads:
                        thread.join()
                    # If the Leader receives a heartbeat message from another Leader with the term number greater than its own,
                    # it becomes a Follower (and also sets its term number to the new leader's one).
                    for pulse in pulses.values():
                        if pulse[0] and (pulse[1] > self.term_number):
                            self._set_state(NODE_STATE.Follower)
            else:
                break

    def _set_state(self, state):
        self.state = state
        self.state_update_event.set()

    def __init__(self, id, addr_port_pair):
        # Events
        self.timer_event = threading.Event()
        self.vote_event = threading.Event()
        self.state_update_event = threading.Event()
        self.not_suspend_event = threading.Event()

        self.timer_event.clear()
        self.vote_event.clear()
        self.state_update_event.clear()
        self.not_suspend_event.clear()

        # Initialize the attributes of the node
        self.term_number = 0
        self.NODES = parseConf(CONFIG_PATH)
        self.majority = ceil(len(self.NODES)/2)
        self.term_number = 0
        self.id = id
        self.leader_id = -1
        self.addr_port_pair = addr_port_pair
        self._set_state(NODE_STATE.Follower)
        self.name = f'Node{str(id)}.:.<{str(addr_port_pair)}>'
        self.timer = None
        self.state_manager = threading.Thread(
            target=self.__state_manager_routine, daemon=True, name=f'State-Manager Node {self.id}')

    def _timeUp_set(self):
        self.timer_event.set()

    def _timeUp_reset(self):
        self.timer_event.clear()

    def reset_timer(self):
        if self.timer:
            self.timer.kill()
        time = self.timer.time_interval
        self.timer = NodeTimer(
            f'NODE-TIMER{self.id}', time, self._timeUp_set)
        self.timer.start()

    def initiate_timer(self):
        if self.timer:
            self.timer.kill()
        time = getTimerInterval()
        self.timer = NodeTimer(
            f'NODE-TIMER{self.id}', time, self._timeUp_set)
        self.timer.start()

    def RequestVote(self, term, candidateId):
        # TODO #2: called by the Candidate during the elections to collect votes
        #     return two values:
        # 1. term number of the server
        # 2. result of voting (True/False)

        # Update the timer, as the server updates it whenever any message is received
        self.reset_timer()
        if term > self.term_number:
            self.term_number = term
            # If the server had term number 1, and received a RequestVote with term 2,
            # it should raise its termnumber to 2, and vote for this candidate.
            # If immediately after that, it receives a RequestVote with term3, it must
            #  also raise its number to 3, and vote for the new candidate
            self.vote_event.clear()
        # TODO: If it receives a RequestVote message, it should vote for a given Candidate, if it has not already voted in that term.
        if term == self.term_number and (not self.vote_event.is_set()):
            self._set_state(NODE_STATE.Follower)
            self.vote_event.set()
            print(SERVER_MSGS.VOTE.format(candidateId))
            # If there are elections now, the function should return information about
            #  the last node that this server votedfor.
            self.leader_id = candidateId
            return (True, self.term_number)
        else:
            return (False, self.term_number)

    def AppendEntries(self, term, leaderId):
        # TODO #5: This function should return two values:
        # 1. term number of the server
        # 2. success (True/False)

        # Update the timer, as the server updates it whenever any message is received
        self.reset_timer()

        # If term >= term number on this server, than success=True. Else, success=False.
        # If, as a result of calling this function, the Leader receives a term number greater than its own term number,
        # that Leader must update his term number and become a Follower.
        if term >= self.term_number:
            self.term_number = term
            if self.state == NODE_STATE.Leader or (not self.leader_id == leaderId):
                self._set_state(NODE_STATE.Follower)
            self.leader_id = leaderId
            # TODO: Every time Follower receives a message from the Leader, it resets the timer
            return (True, self.term_number)
        else:
            return (False, self.term_number)

    def GetLeader(self):
        # TODO #3: called by the client
        # Returns the current Leader id and address.
        # If there are elections now, the function should return information about the last node that this server voted
        # for. If this server has not yet voted on the current term, the function returns nothing.
        print(SERVER_MSGS.GET_LEADER)
        return self.leader_id, self.NODES.get(self.leader_id, ('0.0.0.0', -1))

    def kill(self):
        self._set_state(-1)
        self.timer.kill()
        self.not_suspend_event.clear()

    def run(self):
        self.not_suspend_event.set()
        self.initiate_timer()
        self.state_manager = threading.Thread(
            target=self.__state_manager_routine, daemon=True, name=f'State-Manager Node {self.id}')
        self.state_manager.start()

    def Suspend(self, period):
        # TODO #4: Makes the server sleep for <period> seconds.
        # Used to simulate a short-term disconnection of the server from the system.
        print(SERVER_MSGS.SUSPEND.format(period))
        self.NODES = {}
        self.kill()
        print(SERVER_MSGS.SLEEP.format(period))
        sleep(period)
        self.NODES = parseConf(CONFIG_PATH)
        self.run()
        return True


class RequestHandler(xmlrpc.server.SimpleXMLRPCRequestHandler):
    rpc_paths = (DEFAULT_PATH,)


class MyXMLRPCServer(xmlrpc.server.SimpleXMLRPCServer):
    def __init__(self, addr, logRequests):

        super().__init__(addr, logRequests=logRequests)

    def serve_forever(self):
        self.quit = 0
        while not self.quit:
            self.handle_request()

    def kill(self):
        self.quit = 1
        return 1


if __name__ == '__main__':
    try:
        # INIT BLOCK
        term_number = 0
        timer_interval = getTimerInterval()
        NODES = parseConf(CONFIG_PATH)

        ID = getIDfromArgs(sys.argv[1:])
        ADDR_PORT_PAIR = NODES.get(ID, None)
        if(not ADDR_PORT_PAIR):
            raise BadArgumentException('!NODE-ID NOT IN CONFIGURATION FILE')
        # TODO #1 : BIND TO THE ADDR_PORT PAIR

        print(SERVER_MSGS.START.format(*ADDR_PORT_PAIR))
        node = Node(ID, NODES[ID])
        server = MyXMLRPCServer(
            ADDR_PORT_PAIR, logRequests=False)
        server.register_function(node.RequestVote)
        server.register_function(node.AppendEntries)
        server.register_function(node.GetLeader)
        server.register_function(node.Suspend)
        node.run()
        while True:
            node.not_suspend_event.wait()
            if node.not_suspend_event.is_set():
                server.handle_request()

    except BadConfigException:
        print('INVALID CONFIGURATION.\t>!MAKE SURE THERE EXISITS A VALID "config.conf" FILE IN THE DIRECTORY')
    except BadArgumentException as e:
        print('INVALID ARGUMENT.\t>', e.args[0])
    except KeyboardInterrupt:
        print('KeyboardInterrupt')
    except Exception as e:
        print(e)
