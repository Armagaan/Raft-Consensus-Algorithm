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
	
# import time
# j = 0
# st = time.time()
# v1 = put('apple',5)
# while(j < 100):
# 	v2 = incr("apple", np.random.randint(1000))
# 	v2 = decr("apple", np.random.randint(1000))
# 	j = j + 2
# print(100, time.time()-st)


# j = 0
# st = time.time()
# v1 = put('apple',5)
# while(j < 200):
# 	v2 = incr("apple", 3)
# 	v2 = decr("apple", 3)
# 	j = j + 2
# print(200, time.time()-st)


# j = 0
# st = time.time()
# v1 = put('apple',5)
# while(j < 400):
# 	v2 = incr("apple", 3)
# 	v2 = decr("apple", 3)
# 	j = j + 2
# print(400, time.time()-st)


# j = 0
# st = time.time()
# v1 = put('apple',5)
# while(j < 600):
# 	v2 = incr("apple", 3)
# 	v2 = decr("apple", 3)
# 	j = j + 2
# print(600, time.time()-st)


# j = 0
# st = time.time()
# v1 = put('apple',5)
# while(j < 800):
# 	v2 = incr("apple", 3)
# 	v2 = decr("apple", 3)
# 	j = j + 2
# print(800, time.time()-st)


# j = 0
# st = time.time()
# v1 = put('apple',5)
# while(j < 1000):
# 	v2 = incr("apple", 3)
# 	v2 = decr("apple", 3)
# 	j = j + 2
# print(1000, time.time()-st)



