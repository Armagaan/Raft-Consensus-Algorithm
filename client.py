from client_api import *

v1 = put("apple", 5)
print("apple", v1)
v2 = put("banana", 4)
print("banana", v2)
v3 = incr("apple", 3)
print("apple" ,v3)
v4 = get("apple")
print("apple", v4)
other_server = [("10.184.22.220",12000),("10.184.22.220",12001),("10.184.22.220",12002)]
for s in other_server[:-1]:
	print_log(s)
