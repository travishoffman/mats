from multiprocessing import Process, Pipe

def p2(conn):
	while True:
		conn.send('up and running')

parent, child = Pipe()
p = Process(target=p2, args=(child,))
p.start()

while True:
	print parent.recv()