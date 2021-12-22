import socket
from time import sleep

sock = socket.socket()
sock.setblocking(1)
sock.connect(('192.168.56.1', 9090))

while True:
    msg = input()
    sock.send(msg.encode())
    if msg == 'exit':
        break
    data = sock.recv(1024)
    print(f'Accepted from server: $ {data.decode()}')

sock.close()