from distutils import cmd
import signal
import time
import socket
import random
import threading
import time
import pickle
import types
from msg import decode_client_msg

#MACROS
FOLLOWER = 2
CANDIDATE = 1
LEADER = 0
MIN_TIMEOUT = 6
MAX_TIMEOUT = 10
HEARTBEAT_INTERVAL = 1
INVALID_THREAD = None
INVALID_ADDR = (-1,-1)
START_OF_TIME = 0
HEADER_LEN = 1024

#commands
HB_CMD = b'HB'
VR_CMD = b'VR'
VG_CMD = b'VG'
APP_CMD = b'AP'
ACK_CMD = b'AK'
CR_CMD = b'CR'
PR_CMD = b'PR'

PUT_OP = 'PUT'
GET_OP = 'GET'
INCR_OP = 'INCR'
DECT_OP = 'DECR'

NEW = -1

#server class
class Server:

	def __init__(self, ip, port, other_server, term_num, state = 2):

		#the meta data needed
		self.ip = ip
		self.port = port
		self.leader_addr = INVALID_ADDR
		#self.leader_conn = None
		self.term = term_num
		self.election_timeout = random.randint(MIN_TIMEOUT, MAX_TIMEOUT)
		self.last_heartbeat = time.time()
		
		#this is (ip,port) list
		self.other_server = other_server

		#no connections
		self.connected = []
		for i in range(len(other_server)):
			self.connected.append(False)

		#the sever state
		self.state = state
		if(state > 2 or state < 0):
			self.state = 2

		#the thread numbers running in this server
		self.thread_listen = INVALID_THREAD
		self.thread_write = INVALID_THREAD

		#its time to connect
		#self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.socket.bind((self.ip, self.port))

		# creatae a log table and dictionary
		self.log = []
		self.dict = {}

		#votes recived till now
		self.votes_recived = 0
		self.voted_term = -1
		self.asked_for_votes = -1

		self.commitIndex = NEW
		self.lastApplied = NEW
		self.nextIndex = []
		self.matchIndex = []
		for i in range(len(self.other_server)):
			self.nextIndex.append(-1)
			self.matchIndex.append(-1)

		#for query response
		self.responses = 1
		self.succ_resp = 1
		self.waiting_for_response = False
		self.waiting_for_consistent_response = False
		
	# encoding heartbeat message
	def encode_heartbeat_msg(self):
		data_encode = types.SimpleNamespace(
			cmd = HB_CMD,
			term = self.term
			# should we send leaderID
		)
		encoded_msg = pickle.dumps(data_encode)
		return encoded_msg

	# encoding append message
	def encode_append_msg(self, i, cadd, retry = False):
		if retry:
			data = self.log[max(self.nextIndex[i],0):]
		else:
			data = [self.log[max(self.nextIndex[i],0)]]

		data_encode = types.SimpleNamespace(
			cmd = APP_CMD,
			term = self.term,
			leaderId = (self.ip, self.port),
			prevLogIndex = self.nextIndex[i],
			prevLogTerm = self.log[self.nextIndex[i]][0],
			entries = data,
			leaderCommit = self.commitIndex,
			cadd = cadd,
			retry = retry
		)
		#print(data_encode)
		encoded_msg = pickle.dumps(data_encode)
		return encoded_msg

	# encoding voting messages
	def encode_ack_msg(self, term, status, cadd, retry = False):
		data_encode = types.SimpleNamespace(
			cmd = ACK_CMD,
			term = self.term,
			follower_addr = (self.ip, self.port),
			status = status,
			cadd = cadd,
			retry = retry
			# should we send leaderID
		)
		encoded_msg = pickle.dumps(data_encode)
		return encoded_msg

	# encoding voting messages
	def encode_vote_msg(self, vote_cmd):
		plt = 0
		if(len(self.log) == 0):
			plt = 0
		else:
			plt = self.log[-1][0]
		data_encode = types.SimpleNamespace(
			cmd = vote_cmd,
			term = self.term,
			prevLogIndex = len(self.log) -1,
			prevLogTerm = plt
			# should we send leaderID
		)
		encoded_msg = pickle.dumps(data_encode)
		return encoded_msg

	#encode vote given message
	def encode_vote_msg_given(self,vt):
		data_encode = types.SimpleNamespace(
			cmd = VG_CMD,
			term = vt
		)
		encoded_msg = pickle.dumps(data_encode)
		return encoded_msg

	#encode server response
	def encode_server_response(self, status, res_val=None):
		data_encode = types.SimpleNamespace(
			status = status,
			value = self.leader_addr,
			res_val = res_val
		)
		#print(data_encode)
		encoded_msg = pickle.dumps(data_encode)
		return encoded_msg

	# decoding append message
	def decode_msg(self, encoded_msg):
		return pickle.loads(encoded_msg)

	def append_RPC(self, data, cadd):

		self.log.append((self.term, data))

		try:
			# encoding the append request

			#send the append to each server
			for i,server in enumerate(self.other_server):
				encoded_msg = self.encode_append_msg(i, cadd)
				self.socket.sendto(encoded_msg, server)
				print(f"[ APRC SENT ] to {server} at {time.time()}")
			
			self.waiting_for_response = True

		except Exception as e:
			print(f"[ APPEND REQUEST ] failed")

	def receive_RPC(self, encoded_msg):

		decoded_msg = self.decode_msg(encoded_msg)
		#print(decoded_msg)
		pi = decoded_msg.prevLogIndex
		pt = decoded_msg.prevLogTerm

		# if the term of leader is less than current term then reject
		if decoded_msg.term < self.term:
			return self.term, False

		# if no entry at prevLogIndex

		elif len(self.log) - 1 < pi:
			return self.term, False

		elif(pi != NEW and pt != self.log[pi][0]):
			self.log = self.log[:pi]
			return self.term, False

		else:
			#you are follower now
			self.state = FOLLOWER
			self.leader_addr = decoded_msg.leaderId

			# append all the entries sent by leader
			self.log = self.log[:max(pi,0)] + decoded_msg.entries

			# if leaders commit index is more than followers commit index 
			# then increase the followers commit index
			if decoded_msg.leaderCommit > self.commitIndex:
				self.commitIndex = min(decoded_msg.leaderCommit, len(self.log) -1)
			return self.term, True

	def apply_log(self):

		if self.lastApplied < self.commitIndex:
			self.lastApplied +=1
			term, tuple = self.log[self.lastApplied]
			#print(term, tuple)
			if tuple[0] == "PUT":
				self.dict[tuple[1]] = tuple[2]
			elif tuple[0] == "INCR":
				if tuple[1] not in self.dict.keys():
					self.dict[tuple[1]] = 0
				self.dict[tuple[1]] += tuple[2]
			elif tuple[0] == "DECR":
				if tuple[1] not in self.dict.keys():
					self.dict[tuple[1]] = 0
				self.dict[tuple[1]] -= tuple[2]

			return self.dict[tuple[1]]


	def consistent_logs(self):

		for ind, next_ind in enumerate(self.nextIndex):
			if next_ind < len(self.log)-1:
				try:

					data = self.log[next_ind:]
					# encoding the append request
					encoded_msg = self.encode_append_msg(ind, None, retry = True)
					
					self.socket.sendto(encoded_msg, self.other_server[ind])
					print(f"[ APRC RETRY SENT ] to {server} at {time.time()}")
				except Exception as e:	
					print(f"[ APPEND REQUEST ] failed")

	def _listen(self):

		# Wait for the message to recive
		#	1. EITHER IT WILL BE LEADER WITH DATA
		#	2. IT WILL BE CANDIDATE ASKING FOR VOTE
		# listen for heart beat message and thats it
		while True:

			msg = ''
			#recive the message
			try:
				(msg,addr) = self.socket.recvfrom(HEADER_LEN)
				decoded_msg = self.decode_msg(msg)
				cmd = decoded_msg.cmd

				if(cmd == HB_CMD):
					print(f"[ HEARTBEAT {self.state} ] Recived at {time.time()}")
					if(self.term <= decoded_msg.term):
						self.leader_addr = addr
						self.last_heartbeat = time.time()
						self.term = decoded_msg.term
						self.state = FOLLOWER

				elif(cmd == PR_CMD):
					print('----------')
					print('----------')
					print("Printing Log")
					print(self.log)
					print("Printing state machine")
					print(self.dict)
					print('----------')
					print('----------')

				elif(cmd == VR_CMD):
					
					print(f"[ VOTE REQUEST {self.state} ] Recived at {time.time()} from {addr} {self.term}")

					if(self.state != FOLLOWER and self.term == decoded_msg.term):
						continue

					if(self.voted_term < decoded_msg.term and self.term <= decoded_msg.term):
						#check the log term and index
						myindex = len(self.log)-1
						myterm = 0
						if(myindex > 0):
							myterm = self.log[-1][0]
						if(decoded_msg.prevLogTerm < myterm or (decoded_msg.prevLogTerm == myterm and myindex > decoded_msg.prevLogIndex)):
							continue
						else:	
							encoded_msg = self.encode_vote_msg_given(decoded_msg.term)
							self.socket.sendto(encoded_msg, addr)
							self.voted = addr
							self.voted_term = decoded_msg.term
							self.state = FOLLOWER
							print(f"[ VOTES SENT {self.state} ]  to {addr} at {time.time()}")

				elif(cmd == VG_CMD):

					if(self.state == CANDIDATE):
						if(decoded_msg.term == self.term):
							self.votes_recived = self.votes_recived + 1
							if(self.votes_recived > len(self.other_server)/2):
								self.state = LEADER
								self.nextIndex = [len(self.log)-1]*len(self.other_server)
								self.succ_resp = 1
								self.responses = 1
								self.waiting_for_response = False

							print(f"[ VOTES RECIVED {self.state} ]  from {addr} at {time.time()} total votes: {self.votes_recived}")

				elif cmd == CR_CMD:

					if self.state != LEADER:
						encoded_msg = self.encode_server_response(False)
						try:
							self.socket.sendto(encoded_msg, addr)
							print(f"[ RESPONSE TO CLIENT ] {addr}")
						except Exception as e:
							print(f"[ RESPONSE TO CLIENT ] sending failed {addr}")
					else:
						self.append_RPC((decoded_msg.operation, decoded_msg.variable, decoded_msg.value),addr)

				elif cmd == APP_CMD:

					term, status = self.receive_RPC(msg)
					encoded_msg = self.encode_ack_msg(term, status, decoded_msg.cadd, decoded_msg.retry)

					try:
						self.socket.sendto(encoded_msg, addr)
						print(f"[ ACK SENT ] to {addr}")
					except Exception as e:
						print(f"[ ACK ] sending failed to {addr}")

				elif cmd == ACK_CMD:
					#print(decoded_msg)
					if(self.state == LEADER and decoded_msg.retry):
						if(decoded_msg.term == self.term):
							ind = self.other_server.index(addr)
							if(decoded_msg.status):
								self.nextIndex[ind] = len(self.log)-1
							else:
								self.nextIndex[ind] = max(0, self.nextIndex[ind]-1)

					elif(self.state == LEADER and self.waiting_for_response):
						ind = self.other_server.index(addr)
						#print(decoded_msg)
						#print(self.nextIndex)
						if(decoded_msg.term == self.term):
							self.responses = self.responses + 1
							if(decoded_msg.status):
								self.succ_resp = self.succ_resp + 1
								self.nextIndex[ind] = len(self.log)-1
							else:
								self.nextIndex[ind] = max(0, self.nextIndex[ind]-1)
							if(self.succ_resp > len(self.other_server)/2):
								cadd = decoded_msg.cadd
								self.responses = 1
								self.succ_resp = 1
								self.waiting_for_response = False

								# increase commitIndex
								self.commitIndex +=1
								res_val = self.apply_log()

								encoded_msg = self.encode_server_response(True, res_val)
								self.socket.sendto(encoded_msg, cadd)

							elif(self.responses == len(self.other_server)):
								cadd = decoded_msg.cadd
								self.responses = 1
								self.succ_resp = 1
								self.waiting_for_response = False
								encoded_msg = self.encode_server_response(False, None)
								self.socket.sendto(encoded_msg, cadd)
						
						#print(self.nextIndex)
						

			except Exception as e:
				print(e)
				print(f"[ RECEIVED NOTHING {self.state} ] not reciving anything")

	# the write thread funtion
	def _write(self):

		# while true just send the heartbeat
		while(True):

			# see if you are leader
			if(self.state == LEADER):

				# get the meassage
				header = self.encode_heartbeat_msg()

				#send the heartbeats to each server
				for server in self.other_server:
					self.socket.sendto(header, server)
					print(f"[ HEARTBEAT SENT {self.state} ] sent heartbeat to {server} at {time.time()}")
				self.consistent_logs()
				time.sleep(HEARTBEAT_INTERVAL)

			#are you candidate?
			elif(self.state == CANDIDATE):

				if(self.asked_for_votes < self.term):
					#ask for votes
					msg = self.encode_vote_msg(VR_CMD)
					self.asked_for_votes = self.term

					#for all server send the the vote request
					for server in self.other_server:
						try:
							self.socket.sendto(msg,server)
							print(f"[ VOTE REQUEST {self.state} ] sent vote request to {server} at {time.time()}")
						except Exception as e:
							print(f"[ VOTE REQUEST {self.state} ] cant connect to {server}")
							
	#create the run function
	'''IF LEADER OR CANDIDATE THERE WILL BE TWO THREADS RUNNING FOR LISTENING AND READING
		BUT IF FOLLOWE ONLY LISTEN THREAD WILL RUN'''
	def run(self):

		#set threads
		self.thread_listen = threading.Thread(target = self._listen)
		self.thread_listen.start()
		self.thread_write = threading.Thread(target = self._write)
		self.thread_write.start()

		#add the timeout
		print(f"[ SERVER STARTED {self.state} ] timeout {self.election_timeout}")

		#just run
		while True:

			# are you candidate
			if(self.state == FOLLOWER or self.state == CANDIDATE):

				# now check the last time you recived the heartbeat
				if(time.time() - self.last_heartbeat > self.election_timeout):

					#if you are follower go for the 

					# change the state and go for election
					self.state = CANDIDATE
					self.last_heartbeat = time.time()
					self.term = self.term + 1
					self.election_timeout = random.randint(MIN_TIMEOUT, MAX_TIMEOUT)
					self.votes_recived = 1
					self.voted_term = self.term

				self.apply_log()
				# self.consistent_logs()

			# # just go to sleep
			# time.sleep(self.election_timeout)