import socket
import select
import os


'''
is read a input from the user or an automatic operation on the client?
is it just messages that we are sending?
how does read work?

maybe setup a master server?
connect server with servers
allow clients to connect
send writes to other servers
'''


HOST = '127.0.0.1'  # Localhost
PORT = 58008        # Port 
MASTER_PORT = 58008

messages = {}
send_buffer = {}    # Buffers that stores the sockets that need a reply after they request

client_sockets_list = []   # List of all slient sockets (including server socket)
client_addresses = {} # {socket : addr}
client_ports = {} #{socket : port}
client_dependency = {} #{message: [clients]}

server_sockets_list = []
client_addresses = {} # {socket : addr}
#Start the server
#handles connections from peers
def start_server():
    
    sockets_list = []   # List of all sockets (including server socket)
    socket_addr = {} 

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Create a socket
    server_socket.bind((HOST, PORT))
    server_socket.listen(4)     #Listen for incoming connections
    server_socket.setblocking(False)
    sockets_list.append(server_socket)
    print(f"Server starting on {HOST}:{PORT}")

    #using select to manage the sockets
    while True:
        readable, writable, exceptional = select.select(sockets_list, sockets_list, sockets_list)

        for current_socket in readable:
            if current_socket == self_socket: #establish new connections

                peer_socket, peer_address = self_socket.accept()
                print(f"Connected by {peer_address}")
                socket_addr[peer_socket] = peer_address

                #Set the client socket to non-blocking and add to monitoring list
                peer_socket.setblocking(True)
                sockets_list.append(peer_socket)
            else:
                pass




#Connects to the other servers
def connect_to_server():
    # Create a socket (TCP/IP)
    close_flag = True # flag for if the program closes
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.connect((HOST, PORT))  # Connect to the server

    print(f"client connecting to server {HOST}:{PORT}")

    # Receive a response from the server
    while(close_flag == True):
        commands = []
        print("Commands: ",commands)
        command = input("command: ").lower()

        if(command == "recv"): 
            recv(server_socket)
        elif(command == "send"):
            message = input("message: ")
            send(server_socket, message)
        elif(command == "close"):
            close_client(server_socket)
            close_flag = False
        elif(command == "download"):
            file_name = input("File name: ")
            peer_ports = get_file_location(server_socket, file_name)
            if(peer_ports):
                download_from_peers(server_socket, peer_ports, file_name)
        else:
            print("not a valid command: ",commands)

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
        if(message == "register"):
            #filename = client_socket.recv(1024)
            register(client_socket)
        elif(message == "close"):
            close_socket(client_socket)
        elif(message == "file list"):
            send_list_of_files(client_socket)
        elif(message == "file location"):
            file_name = client_socket.recv(1024).decode('utf-8')
            send_file_location(client_socket, file_name)
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

def register(client_socket):
    pass


#Close the server and all client connections
def close_server(server_socket):
    print("Closing server and all client connections.")
    for addr, client_socket in client_addresses.items():
        client_socket.close()  #Close each client socket
    server_socket.close()  #Close the server socket
    print("Server closed.")


#handles closing sockets
def close_socket(client_socket):
    if client_socket in send_buffer:
        del send_buffer[client_socket]

    #remove the address from all files
    if client_socket in client_ports:
        for file_name in files:
            files[file_name].remove_user_from_chunk(client_ports[client_socket])

    client_socket.shutdown(socket.SHUT_RDWR)
    client_socket.close()
    print(f"Client {client_addresses[client_socket]} disconnected")
    sockets_list.remove(client_socket)
    del client_addresses[client_socket]


def send_confirmation(client_socket):
    client_socket.sendall("confirm".encode('utf-8'))

def debugger(client_socket):
    print(sockets_list)
    print("using ", client_socket)

if __name__ == '__main__':
    PORT = int(input("User port (0 - 65535): " ))
    thread1 = threading.Thread(target=connect_to_server)
    thread2 = threading.Thread(target=start_server)
    thread2.start()
    thread1.start()