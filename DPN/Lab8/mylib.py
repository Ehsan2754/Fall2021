import random
CONFIG_PATH = 'config.conf'
PROXY_URI = 'http://{0}:{1}/'
DEFAULT_PATH = '/'
TIME_RANGE = (150, 300)


class SERVER_MSGS:
    START = 'Server is started at {0}:{1}'
    SLEEP = 'Sleeping for {0} seconds.'
    VOTE = 'Voted for node {0}'
    DEAD_LEADER = 'The leader is dead'
    FOLLOWER_STATUS = 'I am a follower. Term: {0}'
    CANDIDATE_STATUS = 'I am a candidate. Term: {0}'
    LEADER_STATUS = 'I am a leader. Term: {0}'
    GET_LEADER = 'Command from client: getleader'
    SUSPEND = 'Command from client: suspend {0}'
    VOTE_RECEIVED = 'Votes received'


class CLIENT_MSGS:
    START = 'The client starts'
    LEADER_ADDR = "{0} {1}:{2}"
    PROXY_NA = 'The server {0}:{1} is unavailable.'
    EXIT = 'The client ends'


# My exception for bad argument
class BadArgumentException(Exception):
    pass

# My exception for bad argument


class BadConfigException(Exception):
    pass

# random time generator 
def getTimerInterval():
    timeInterval = (random.randint(*TIME_RANGE))/100
    return timeInterval

# Parses the configuration file


def parseConf(path):
    try:
        EMPTY_LINE = ''
        pairs = {}
        CONF = open(path, 'r')
        line = CONF.readline()
        while(line):
            node = line.split()
            pairs[int(node[0])] = (node[1], int(node[2]))
            line = CONF.readline()
        CONF.close()
        return pairs
    except:
        raise BadConfigException()


# Extracts ID from the args
def getIDfromArgs(args):
    if len(args) > 0:
        if args[0].isnumeric():
            return int(args[0])
    else:
        raise BadArgumentException('!INPUT ARGUMENT IS NOT VALID.')

# NODE STATES


class NODE_STATE:
    Follower = 'Follower'
    Candidate = 'Candidate'
    Leader = 'Leader'