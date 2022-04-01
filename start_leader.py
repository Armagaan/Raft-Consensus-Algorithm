from raft_2 import Server, FOLLOWER, CANDIDATE, LEADER

#other_server = [("10.184.12.210",12000),("10.184.12.210",12001),("10.184.12.210",12002),("10.184.12.210",12003)]
other_server = [("10.17.3.66",12000),("10.17.8.80",12001),("10.17.10.20",12002)]
s = Server(other_server[0][0], other_server[0][1], other_server[1:], 0, state = LEADER)
s.run()