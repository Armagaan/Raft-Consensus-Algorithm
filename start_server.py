from server import Server

ip = "10.17.3.66"
port = "1234"
other_ip = ["10.17.10.20", "10.17.8.80"]
initial_term_num =0

# create a node
node = Server(ip, port, other_ip, term_num = initial_term_num)

# initialise the node as follower
node.initialise_server()