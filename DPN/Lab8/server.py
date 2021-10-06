# configuring my log env
from asyncio.windows_events import SelectorEventLoop
import concurrent.futures
from time import sleep
import xmlrpc.client
import random
import threading
import sys
from math import ceil
from mylib import *
import logging
from logging import debug
logging.basicConfig(level=logging.DEBUG)
# other imports


def getTimerInterval():
    timeInterval = random.randint(*TIME_RANGE)/1000
    debug(f"{timeInterval} sec.")
    return timeInterval


class Node():
    class NodeTimer(threading.Thread):
        def __init__(self, name, timeUp_set, timeUp_reset, set_state):
            self.dead = False
            self.timeUp_set = timeUp_set
            self.timeUp_reset = timeUp_reset
            super().__init__(name=name, daemon=True)
        def kill(self):
            self.dead = True
        def run(self):
            while not self.dead:
                time = getTimerInterval()
                self.timeUp_reset()
                sleep(time)
                if not self.dead:
                    self.timeUp_set()
                    # TODO: If the timer is up, Follower becomes a Candidate.
                    self.set_state(NODE_STATE.Candidate)
            return super().run()

    def __election_routine(self, node_id):
        res = None
        try:
            proxy = xmlrpc.client.ServerProxy(
                PROXY_URI.format(*self.NODES[node_id]))
            res = proxy.RequestVote(self.term_number, self.id)
        except ConnectionRefusedError as e:
            res = (False, -1)
        return res

    def __state_manager_routine(self):
        self.state_update_event.wait()
        if self.state == NODE_STATE.Follower:
            self.reset_timer
        if self.state == NODE_STATE.Candidate:
            # TODO : if node became a candidate it increments its term number and resets its timer
            self.term_number += 1
            current_term_number = self.term_number
            votes = {}
            self.vote_event.set()
            with concurrent.futures.ThreadPoolExecutor() as executor:
                voters = list(self.NODES.keys())
                voters.remove(self.id)
                futures = [executor.submit(
                    self.__election_routine, voter_id) for voter_id in voters]
                votes = {voter_id: f.result for voter_id,
                         f in enumerate(voters, futures)}
                votes[self.id] = (True, self.term_number)  # Voting for itself
            num_votes = 0
            for vote in votes.values():
                if vote[0]:
                    num_votes += 1
            if num_votes >= self.majority:
                return True
            else:
                return False

    def _set_state(self, state):
        self.state = state
        self.state_update_event.set()

    def __init__(self, id, addr_port_pair):
        # Events
        self.timer_event = threading.Event()
        self.leader_req_received_event = threading.Event()
        self.vote_event = threading.Event()
        self.state_update_event = threading.Event()

        self.timer_event.clear()
        self.leader_req_received_event.clear()
        self.vote_event.clear()
        self.state_update_event.clear()

        # Initialize the attributes of the node
        self.term_number = 0
        self.timer_interval = getTimerInterval()
        self.NODES = parseConf(CONFIG_PATH)
        self.majority = ceil(len(self.NODES))
        self.term_number = 0
        self.id = id
        self.leader_id = -1
        self.addr_port_pair = addr_port_pair
        self.state = NODE_STATE.Follower
        self.name = f'Node{str(id)}.:.<{str(addr_port_pair)}>'
        self.timer = self.NodeTimer(
            f'NODE-TIMER{self.id}', self._timeUp_set, self._timeUp_reset, self._set_state)
        self.timer.start()

    def _timeUp_set(self):
        self.timer_event.set()

    def _timeUp_reset(self):
        self.timer_event.clear()

    def reset_timer(self):
        self.timer.kill()
        self.timer = self.NodeTimer(
            f'NODE-TIMER{self.id}', self._timeUp_set, self._timeUp_reset)
        self.timer.start()

    def RequestVote(self, term, candidateId):
        # TODO #2: called by the Candidate during the elections to collect votes
        #     return two values:
        # 1. term number of the server
        # 2. result of voting (True/False)
        if term > self.term_number:
            self.term_number = term
            self.vote_event.clear()
        # TODO: If it receives a RequestVote message, it should vote for a given Candidate, if it has not already voted in that term.
        if term == self.term_number and (not self.vote_event.is_set()):
            self._set_state(NODE_STATE.Follower)
            self.vote_event.set()
            return (True, self.term_number)
        else:
            return (False, self.term_number)

    def AppendEntries(self, term, leaderId):
        # TODO #5: This function should return two values:
        # 1. term number of the server
        # 2. success (True/False)
        # If term >= term number on this server, than success=True. Else, success=False.
        # If, as a result of calling this function, the Leader receives a term number greater than its own term number,
        # that Leader must update his term number and become a Follower.
        if term >= self.term_number:
            self.term_number = term
            self._set_state(NODE_STATE.Follower)
            self.leader_id = leaderId
            # TODO: Every time Follower receives a message from the Leader, it resets the timer
            return True
        else:
            return False

    def GetLeader(self):
        # TODO #3: called by the client
        # Returns the current Leader id and address.
        # If there are elections now, the function should return information about the last node that this server voted
        # for. If this server has not yet voted on the current term, the function returns nothing.
        return self.leader_id, self.NODES[self.leader_id]

    def Suspend(period):
        # TODO #4: Makes the server sleep for <period> seconds.
        # Used to simulate a short-term disconnection of the server from the system.
        pass


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

        debug(NODES)
        debug(ID)
        debug(ADDR_PORT_PAIR)

        # TODO #1 : BIND TO THE ADDR_PORT PAIR
        print(SERVER_MSGS.START.format(*ADDR_PORT_PAIR))
        n = Node(1, NODES[1])
        sleep(1)

        def tar():
            sleep(1000)
        t = threading.Thread(target=tar, name='TEST1', daemon=True)
        t.start()
        t = threading.Thread(target=tar, name='TEST1', daemon=True)
        t.start()

    except BadConfigException:
        print('INVALID CONFIGURATION.\t>!MAKE SURE THERE EXISITS A VALID "config.conf" FILE IN THE DIRECTORY')
    except BadArgumentException as e:
        print('INVALID ARGUMENT.\t>', e.args[0])
