import socket
import select
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
PORT = 58008        # Port 
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

    socket_addr = {} 
    sockets_list = []
    
    self_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Create a socket
    self_socket.bind((HOST, PORT))
    self_socket.listen(4)     #Listen for incoming connections
    self_socket.setblocking(False)
    sockets_list.append(self_socket)
    print(f"Server starting on {HOST}:{PORT}")

    #using select to manage the sockets
    while True:
        readable, writable, exceptional = select.select(sockets_list, sockets_list, sockets_list)

        for current_socket in readable:
            if current_socket == self_socket: #establish new connections

                peer_socket, peer_address = self_socket.accept()
                peer_socket.setblocking(True)
                socket_addr[peer_socket] = peer_address
                sockets_list.append(peer_socket)
                print(f"Connected by {peer_address}")

                handler = (current_socket.recv(1024)).decode('utf-8')
                if(handler == "server"):
                    server_sockets_list.append(peer_socket)
                elif (handler == "client"):
                    client_sockets_list.append(peer_socket)
                
            else:
                handler = (current_socket.recv(1024)).decode('utf-8') 
                if(handler == "server"):
                    server_handler(current_socket)
                elif (handler == "client"):
                    client_handler(current_socket)

def new_server_connection():
    pass

def connect_to_master():
    master_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    master_socket.connect((HOST, PORT))  # Connect to the server
    
    #send port to master
    master_socket.sendall(PORT.to_bytes(8, byteorder='big'))

    #recv all other server ports
    num_of_servers = int.from_bytes(master_socket.recv(1024), byteorder='big')
    for i in range(num_of_servers):
        server_sockets_list += [int.from_bytes(master_socket.recv(1024), byteorder='big')]


def server_handler(server_socket):
    while True:
        readable, writable, exceptional = select.select(server_sockets_list, server_sockets_list, server_sockets_list)

        for current_socket in readable:
            
def client_handler(client_socket):
    while True:
        readable, writable, exceptional = select.select(client_sockets_list, client_sockets_list, client_sockets_list)

        for current_socket in readable:


#Connects to the other servers
def connect_to_server():
    #connect to all servers
    for port in server_ports:
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.connect((HOST, port))  # Connect to the server
        server_sockets_list += [server_socket]
        print(f"connecting to server {HOST}:{port}")


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

#Receive commands from the client
def recv(client_socket):
    try:
        data = client_socket.recv(1024)
        if data:
            print(f"Received from {client_addresses[client_socket]}: {data.decode('utf-8')}")
        else:
            close_socket(client_socket)
        
        message = data.decode('utf-8')
        message = message.strip()
        #takes in commands from the user:
        if(message == "close"):
            close_socket(client_socket)
        elif(message == "store hash"):
            file_name = client_socket.recv(1024).decode('utf-8')
            chunk_hashes = client_socket.recv(1024).decode('utf-8').split(',')
            files[file_name].store_hashes(chunk_hashes)
        elif(message == "verify chunk"):
            send_confirmation(client_socket)
            file_name = client_socket.recv(1024).decode('utf-8')
            chunk_num = int.from_bytes(client_socket.recv(8), byteorder='big')
            print(chunk_num)
            hash = files[file_name].get_hash(chunk_num)
            print(hash)
            client_socket.sendall(hash.encode('utf-8'))
            print("sending verify hash")
        elif(message == "download"):
            file_name = client_socket.recv(1024).decode('utf-8')
            send_download_info(client_socket, file_name)
    except ConnectionError as e:
        #Handle client disconnection
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
    PORT = int(input("User port (0 - 65535): " ))
    thread1 = threading.Thread(target=start_server)
    thread2 = threading.Thread(target=client_handler)
    thread3 = threading.Thread(target=server_handler)
    thread1.start()
    thread2.start()
    thread3.start()