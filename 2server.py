import socket, random, csv, hashlib, threading, time, os


def s_send(sock, data, service_data = ''):
    length = str(len(data + service_data))
    length = '0' * (9-len(length)) + length
    data = (length + service_data + data).encode()
    sock.send(data)

def s_recv(sock):
    length = int(sock.recv(9).decode())
    data = sock.recv(length).decode()
    return data

def print_log(*data):
    data = ' '.join((str(el) for el in data))
    global LOCK, LOG, log_file
    if LOG:
        with LOCK:
            print(data)
            with open(log_file, 'a+') as file:
                file.write(data+'\n')

socket.socket.s_send = s_send
socket.socket.s_recv = s_recv


def register(conn, addr, file_list):
    global pass_file
    while True:
        conn.s_send('Create a login: ', '@$$~')
        login = conn.s_recv()
        for row in file_list:
            if row[1] == login:
                print_log('That login is already exist.')
        else:
            break
    
    conn.s_send('Create a password: ', '$$$~')
    password = conn.s_recv()
    ip_address = hashlib.md5(addr[0].encode()).hexdigest()
    password = hashlib.md5(password.encode()).hexdigest()
    row = ip_address, login, password
    with LOCK:
        with open(pass_file, 'a+', newline = '') as users:
            writer = csv.writer(users, delimiter = ';')
            writer.writerow(row)

    conn.s_send('Registration succeed.')
    print_log(f'{addr[0]} has registered.')  
    return login, password


def authentification(conn, addr, password, attempts = 5):
    global active_connections
    if attempts == 0:
        conn.s_send('You entered invalid password for 5 times. Try again later.')
        return False

    conn.s_send('Enter your password: ', '$$$~')
    recv_pswd = conn.s_recv()

    if password == hashlib.md5(recv_pswd.encode()).hexdigest():
        conn.s_send('Logged in successfully.', '@$@~')
        print_log(f'{addr[0]} logged in.')
        active_connections.append(conn)
        return True

    else:
        conn.s_send('Invalid password.')
        return authentification(conn, addr, password, attempts-1)
    

def listening(conn, addr):
    global active_connections, LOCK, pass_file, message_history
    
    with LOCK:
        with open(pass_file, 'a+', newline = '') as users:
            users.seek(0,0)
            reader = csv.reader(users, delimiter = ';')
            file_list = list(reader)
    try:
        for row in file_list:
            if row[0] == hashlib.md5(addr[0].encode()).hexdigest():
                login, password = row[1], row[2]
                break
        else:
                login, password = register(conn, addr, file_list)

        if authentification(conn, addr, password):
            while True:
                data = conn.s_recv()
                with LOCK:
                    with open(message_history, 'a+', newline = '') as msg_hst:
                        writer = csv.writer(msg_hst, delimiter = ';')
                        writer.writerow((addr[0], login, data))
                data = login + " &~: " + data
                print_log(data)
                conn_list = list(active_connections)
                conn_list.remove(conn)
                for clnt_conn in conn_list:
                    clnt_conn.s_send(data)
        else:
            print_log('Authentification failed.')
            conn.close()

    except (ConnectionAbortedError, ConnectionResetError, ValueError) as err:
        active_connections.remove(conn)
        print_log(err, addr[0])
        
    
    print_log(f'Connection with {addr[0]} closed.')


def connecting(sock):
    global LOCK, LISTEN
    while True:
        if LISTEN:
            conn, addr = sock.accept()
            print_log(f'Client {addr[0]} has connected.')
            threading.Thread(target = listening, args = (conn, addr), daemon = True).start()
        


def bind(sock, con_port):
    while True:
        try:
            sock.bind(('', con_port))
            break
        except OSError as oserr:
            print_log("{} (port {} has been taken.)".format(oserr, con_port))
            con_port = random.randint(1024,65535)
    sock.listen(0)
    print_log('Server is running at the port {}.'.format(con_port))



active_connections = []
LOCK = threading.Lock()
LISTEN = True
LOG = True
con_port = 9090
pass_file = "users.csv"
message_history = f'msg_hst_{time.time()}.csv'
log_file = f'log_{time.time()}.txt'



sock = socket.socket()
sock.setblocking(True)

bind(sock, con_port)

threading.Thread(target = connecting, args = (sock, ), daemon = True).start()
commands = '''Shutdown - to shutdown the server.
Clear file - to clear  clients list.
Stop listen - to stop listening the port.
Start listen - to start listening the port.
Stop log - to stop printing logs.
Start log - to start printing logs.
Clear log - to clear the log file.'''
print(commands)

while True:
    cmd = input()
    if cmd == 'shutdown':
        break
    elif cmd == 'clear file':
        with open(pass_file, 'w', newline = '') as users:
            pass
    elif cmd == 'stop listen':
        LISTEN = False
    elif cmd == 'start listen':
        LISTEN = True
    elif cmd == 'stop log':
        LOG = False
    elif cmd == 'start log':
        LOG = True
    elif cmd == 'clear log':
        if os.name == 'nt':
            os.system('cls')
        else:
            os.system('clear')
        with open(log_file, 'w'):
            pass

sock.close()