import socket
import select
import os


'''
is read a input from the user or an automatic operation on the client?
is it just messages that we are sending?
how does read work?

'''


HOST = '127.0.0.1'  # Localhost
PORT = 58008        # Port 

send_buffer = {}    # Buffers that stores the sockets that need a reply after they request
sockets_list = []   # List of all sockets (including server socket)
files = {}          # List of files {file name : file object}
DEFAULT_CHUNK_SIZE = 4096
busy_socket_recv = []

#Dictionary to store multiple addresses
client_addresses = {} # {socket : addr}
client_ports = {} #{socket : port}


#Start the server
def start_server(Selfport):
    
    sockets_list = []   # List of all sockets (including server socket)
    socket_addr = {} 

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Create a socket
    server_socket.bind((HOST, Selfport))
    server_socket.listen(4)     #Listen for incoming connections
    sockets_list.append(server_socket)
    server_socket.setblocking(False)
    print(f"Server starting on {HOST}:{Selfport}")

    #using select to manage the sockets
    while True:
        readable, writable, exceptional = select.select(sockets_list, sockets_list, sockets_list)
        pass


#Connects to the server socket
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
        #closes
        elif(message == "chunk register"):
            #filename = client_socket.recv(1024)
            chunk_register(client_socket)
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

    

def register(client_socket):
    pass

def chunk_register(client_socket):
    file_name = (client_socket.recv(1024)).decode('utf-8')                  #recvs filename
    send_confirmation(client_socket)
    chunk_num = int.from_bytes(client_socket.recv(8), byteorder='big')
    file_size = int.from_bytes(client_socket.recv(8), byteorder='big')   #file size
    client_port = int.from_bytes(client_socket.recv(8), byteorder='big') #the port of the client

    client_ports[client_socket] = client_port
    #register new file or adds the user as a file holder
    if file_name in files:
        files[file_name].chunk_register(client_port, chunk_num)
    else:
        newfile = File(file_name, file_size, client_port)
        newfile.chunk_register(client_port, chunk_num)
        files[file_name] = newfile
        print("New file: ", file_name)

#sends the user the info of where to get download from
def send_download_info(client_socket, file_name):
    client_socket.sendall(DEFAULT_CHUNK_SIZE.to_bytes(8, byteorder='big'))
    num_of_chunks = files[file_name].get_num_of_chunks()
    client_socket.sendall(num_of_chunks.to_bytes(8, byteorder='big'))
    print(f"download info sent to {client_addresses[client_socket]}")

#receives a file
def receive_file(client_socket, file_name):
    #Receive the file size from the server
    file_size_data = client_socket.recv(8)  #Expecting 8 bytes for file size
    file_size = int.from_bytes(file_size_data, byteorder='big')
    print(f"Receiving file of size: {file_size} bytes")

    #Start receiving the file in chunks
    received_size = 0   #total data received

    with open(file_name, 'wb') as file:
        while received_size < file_size:
            remaining_size = file_size - received_size
            chunk_size = min(1024, remaining_size)
            chunk = client_socket.recv(chunk_size)
            
            if not chunk:  #Connection closed before the expected file size
                break

            file.write(chunk)
            received_size += len(chunk)

            print(f"Received {received_size}/{file_size} bytes")

    if received_size == file_size:
        print(f"File {file_name} received successfully")

        #chunks = split_file_into_chunks(file_name, DEFAULT_CHUNK_SIZE)
        newfile = File(file_name, file_size, client_addresses[client_socket])
        files[file_name] = newfile
    else:
        print(f"Error: received only {received_size}/{file_size} bytes")


def send_file_location(client_socket, file_name):

    #check if its in the archived file
    if (file_name in files):
        file_locations = files[file_name].get_file_locations()

        #converts the integers to strings
        str_list = []
        for num in file_locations:
            str_list.append(str(num))

        data_list = ','.join(str_list)
        client_socket.sendall(data_list.encode('utf-8'))
        print("Sending location")
    else:               #no files with this name exists
        client_socket.sendall("NULL".encode('utf-8'))
        print("Not a valid file name")        

def send_list_of_files(client_socket):
    file_list = list(files.keys())
    num_of_files = len(file_list)

    out=[f"Number of files: {num_of_files}"]
    
    for file in file_list:
        out.append(f"File Name: {file} Size of file: {files[file].file_size}")
    
    data_list = ';'.join(out)
    data = data_list.encode('utf-8')
    client_socket.sendall(data)

# Send chunk data and hash
def send_chunk(client_socket, file_name, chunk_num):
    file = files[file_name]
    chunk_hash = file.get_chunk_hash(chunk_num)
    
    with open(file_name, 'rb') as f:
        f.seek(chunk_num * DEFAULT_CHUNK_SIZE)
        chunk = f.read(DEFAULT_CHUNK_SIZE)
        client_socket.sendall(chunk)  # Send chunk data
        client_socket.sendall(chunk_hash.encode('utf-8'))  # Send chunk hash
        print(f"Sent chunk {chunk_num} and hash {chunk_hash} to {client_addresses[client_socket]}")


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
    start_server()