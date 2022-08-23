# Raft Consensus Algorithm

[Ongaro, Diego, and John Ousterhout. "In search of an understandable consensus algorithm." 2014 USENIX Annual Technical Conference (Usenix ATC 14). 2014.](https://raft.github.io/raft.pdf)

## NOTE
- We have not implemented log compaction.
- Before running the tests, do the following:
  - Change `other_server` list in `start_follower.py` with the IPs of the machines you are testing with.
  - Change the leader's address in `client.py` to one of the addresses in the `other_server` list.
  - Change addr to the IP of the server on which you will run `client.py`

## LIST OF FILES
`raft_2.py`: Contains the server class and all the methods which make up raft's server side.

`msg.py`: Contains the encoder and decoder functions for the client to use. They are used in `client.py`

`client_api.py`: Contains commands used by client to interact with raft.

`client.py`: The clinet calls this script to issue requests.

`start_follower.py`: Starts the servers in follower state.

## USAGE OF INDIVIDUAL FILES
`start_follower.py`: `python3 start_follower.py [id]`

`[id]`: It is the index of the server's IP in the `other_server`.

`client.py`: `python3 client.py`

## TEST CASES

### SETUP THE SYSTEM
1. Set `other_server = [("10.17.3.66",12000),("10.17.8.80",12001),("10.17.10.20",12002)]` in `start_follower.py`.
2. Set leader = ("10.17.8.80", 12001) 
3. Set addr = ("x.x.x.x", ppppp). This will be the VM from which you run `client.py`.
4. Run `start_leader.py 0` on VM with the following IP: `10.17.3.66"`
5. Run `start_follower.py 1` on VM with the following IP: `10.17.8.80"`
6. Run `start_follower.py 2` on VM with the following IP: `10.17.10.20"`

### LEADER CRASH TO CHECK ELECTION
1. Setup the system.
2. Use `ctrl+c` KeyboardInterrupt on the leader's VM to crash the leader.
3. Watch the console screen for voting to start. You will see a msg like this: `[ VOTE REQUEST ] sent request to (x.x.x.x, ppppp) at <time>` on one of the followers.
4. One of the followers will become a leader and start sending heartbeats.
5. Restart the leader by running `python3 start_leader.py 0` on VM with the following IP: `10.17.3.66"`
6. It thinks it is still the leader and therefore sends heartbeats but gets rejected by the follwers. It receives information about the new leader from his heartbeats and demotes itself.

### FOLLOWER CRASH TO SEE LEADER BEHAVIOUR
1. Setup the system.
2. Use `ctrl+c` KeyboardInterrupt on the leader's VM to crash one of the followers.

### STATE MACHINE CONSISTENCY CHECK
1. Setup the system.
2. Use `ctrl+c` KeyboardInterrupt to crash any server.
3. Run `client.py`.
4. Restart the crashed server after `client.py` has finished execution.
5. Open Python3 IDE.
6. Import `client_api.py` and run `client_api.print_log(<crashed_server's_ip>, <crashed_server's port>)`
7. Verify the answer by comparing it by running the above command for other servers.

### LOAD
1. Setup the system.
2. Uncomment the for loop for the command which you'd like to time.
3. Run `client.py`.
