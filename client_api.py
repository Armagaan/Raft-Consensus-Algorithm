import socket
import msg

leader = ("10.17.8.80", 12001)
addr = ("10.17.8.80", 12010)

# leader = ("10.184.22.220",12000)
# addr = ("10.184.22.220",12010)

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(addr)

PUT_OP = 'PUT'
GET_OP = 'GET'
INCR_OP = 'INCR'
DECR_OP = 'DECR'
MAX_TRIES = 3
RESPONSE_LEN = 1024

def send_command(encode_message, try_no):

	global leader
	if(try_no >= MAX_TRIES):
		return None
	try:
		sock.sendto(encode_message, leader)
		(response,addr) = sock.recvfrom(RESPONSE_LEN)
		decoded_resp = msg.decode_server_response(response)
		if(not decoded_resp.status):
			leader = decoded_resp.value
			return send_command(encode_message,try_no+1)
		else:
			return decoded_resp.res_val
	except Exception as e:
		print(e)
		return send_command(encode_message,try_no+1)

def put(k,v):
	encode_message = msg.encode_client_msg(PUT_OP, k, v)
	return send_command(encode_message,0)

def get(k):
	encode_message = msg.encode_client_msg(GET_OP, k)
	return send_command(encode_message,0)

def incr(k,v):
	encode_message = msg.encode_client_msg(INCR_OP, k, v)
	return send_command(encode_message,0)

def decr(k,v):
	encode_message = msg.encode_client_msg(DECR_OP, k, v)
	return send_command(encode_message,0)

def print_log(addr):
	encode_message = msg.encode_client_msg(DECR_OP,'','',debug=True)
	sock.sendto(encode_message, addr)