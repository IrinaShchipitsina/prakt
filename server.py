import socket, threading, sys

def acceptance(conn, addr):
	while True:
		try:
			data = conn.recv(1024)
		except (ConnectionResetError, ConnectionAbortedError):
			print(f'Client {addr} aborted connection.')
			raise
		print(f'Accepted from {addr}:$ {data.decode()}')
		conn.send(data)


sys.tracebacklimit = 0
sock = socket.socket()
sock.bind(('', 9090))
sock.listen(0)


while True:
	conn, addr = sock.accept()
	print(f'Connected: {addr}.')
	threading.Thread(target = acceptance, args = (conn, addr), daemon = True).start()