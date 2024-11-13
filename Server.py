import socket
import select
import threading
import os


'''
is read a input from the user or an automatic operation on the client?
is it just messages that we are sending?
how does read work?

 - maybe setup a master server?
 - connect server with servers
 - allow clients to connect
 - recv reads and writes from clients
 - send writes to other servers

 dependency lists/recving from other servers
 - add a delaying function
 - add a individual depedency list for messages
 - print out recvs


'''

'''
class Client:
    def __init__(self):
        dependency_list = []
'''

HOST = '127.0.0.1'  # Localhost
SERVER_PORT = 58008        # Port and Port + 1 will be used for client server connections
SERVER_CLIENT_PORT = 0
MASTER_PORT = 58008

messages = {}
send_buffer = {}    # Buffers that stores the sockets that need a reply after they request

client_sockets_list = []   # List of all slient sockets (including server socket)
client_ports = []       #[port]
client_dependency = {}  #{message: [clients]}
client_addresses = {}   # {socket : addr}

server_sockets_list = []    #[socket]
server_ports = []           #[port]
server_addresses = {} # {socket : addr}


#Start the server
def start_server():

    connect_to_master()
    connect_to_server()


def connect_to_master():
    global server_ports

    master_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    master_socket.connect((HOST, MASTER_PORT))  # Connect to the server
    
    #recv all other server ports
    num_of_servers = int.from_bytes(master_socket.recv(1024), byteorder='big')
    for i in range(num_of_servers):
        server_ports += [int.from_bytes(master_socket.recv(1024), byteorder='big')]

    #send port to master
    master_socket.sendall(SERVER_PORT.to_bytes(8, byteorder='big'))


#Connects to the other servers
def connect_to_server():
    global server_sockets_list
    #connect to all servers
    print("server ports: ", server_ports)
    for port in server_ports:
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.connect((HOST, port))  # Connect to the server
        server_sockets_list.append(server_socket)
        print(f"connecting to server {HOST}:{port}")

    

#reads from other server
def server_handler():
    global server_sockets_list
    
    self_server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Create a socket
    server_sockets_list.append(self_server_socket)
    self_server_socket.bind((HOST, SERVER_PORT))
    self_server_socket.listen(4)     #Listen for incoming connections
    self_server_socket.setblocking(False)
    print(f"Server starting on {HOST}:{SERVER_PORT}")

    #using select to manage the sockets
    while True:
        readable, writable, exceptional = select.select(server_sockets_list, server_sockets_list, server_sockets_list)

        for current_socket in readable:
            if current_socket == self_server_socket: #establish new connections

                peer_socket, peer_address = self_server_socket.accept()
                peer_socket.setblocking(True)
                server_sockets_list.append(peer_socket)
                server_addresses[peer_socket] = peer_address
                print(f"Connected by server: {peer_address}")
            else:
                message = current_socket.recv(1024).decode('utf-8')
                print("Server message: ", message)

#writes to this server
#then broadcasts to other servers
def client_handler():
    global client_sockets_list

    client_server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Create a socket
    client_sockets_list.append(client_server_socket)
    client_server_socket.bind((HOST, SERVER_CLIENT_PORT))
    client_server_socket.listen(4)     #Listen for incoming connections
    client_server_socket.setblocking(False)
    print(f"client server starting on {HOST}:{SERVER_CLIENT_PORT}")

    while True:
        readable, writable, exceptional = select.select(client_sockets_list, client_sockets_list, client_sockets_list)

        for current_socket in readable:
            if current_socket == client_server_socket: #establish new connections
                peer_socket, peer_address = client_server_socket.accept()
                peer_socket.setblocking(True)
                client_sockets_list.append(peer_socket)
                client_addresses[peer_socket] = peer_address
                print(f"Connected by client: {peer_address}")
            else:
                client_command = current_socket.recv(1024).decode('utf-8')
                print("Client operation: ", client_command)


#Send a message to a specific client
def send(client_socket, message):
    try:
        print(client_socket)
        client_socket.sendall(message.encode('utf-8'))
        print(f"sent to {client_addresses[client_socket]}: {message}")

        if client_socket in send_buffer:
            del send_buffer[client_socket]
        
    except ConnectionError as e:
        close_socket(client_socket)

def write():
    pass

def read():
    pass

#Close the server and all client connections
def close_server(server_socket):
    print("Closing server and all client connections.")
    for addr, client_socket in client_addresses.items():
        client_socket.close()  #Close each client socket
    server_socket.close()  #Close the server socket
    print("Server closed.")


#handles closing sockets
def close_socket(client_socket, server_socket):
    if client_socket in send_buffer:
        del send_buffer[client_socket]

    client_socket.shutdown(socket.SHUT_RDWR)
    client_socket.close()
    print(f"Client {client_addresses[client_socket]} disconnected")
    client_sockets_list.remove(client_socket)
    del client_addresses[client_socket]


def send_confirmation(client_socket):
    client_socket.sendall("confirm".encode('utf-8'))

def debugger(client_socket):
    print(server_sockets_list)
    print("using ", client_socket)

if __name__ == '__main__':
    SERVER_PORT = int(input("User port (0 - 65535): " ))
    SERVER_CLIENT_PORT = SERVER_PORT + 1
    thread1 = threading.Thread(target=start_server)
    thread2 = threading.Thread(target=client_handler)
    thread3 = threading.Thread(target=server_handler)
    thread1.start()
    thread2.start()
    thread3.start()