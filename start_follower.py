import sys
from raft_2 import Server, FOLLOWER, CANDIDATE, LEADER


#other_server = [("10.184.22.220",12000),("10.184.22.220",12001),("10.184.22.220",12002)]
other_server = [("10.17.3.66",12000),("10.17.8.80",12001),("10.17.10.20",12002)]
i = int(sys.argv[1])
s = Server(other_server[i][0], other_server[i][1], other_server[:i]+other_server[i+1:], 0, state = FOLLOWER)
s.run()