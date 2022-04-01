import pickle
import types
CR_CMD = b'CR'
PR_CMD = b'PR'


def decode_client_msg(encoded_msg):
	return pickle.loads(encoded_msg)

# this is for client to encode the message
def encode_client_msg(operation, variable, value = None, debug = False,):
	if(debug):
		data_encoded = types.SimpleNamespace(
		cmd = PR_CMD,
		variable = variable,
		operation = operation,
		value = value)
		encoded_msg = pickle.dumps(data_encoded)
		return encoded_msg

	data_encoded = types.SimpleNamespace(
		cmd = CR_CMD,
		variable = variable,
		operation = operation,
		value = value)
	encoded_msg = pickle.dumps(data_encoded)
	return encoded_msg

#encode the server response
#{success: boolean, value: [value | leader_ip]}
#decode server response
def decode_server_response(encoded_msg):
	return pickle.loads(encoded_msg)