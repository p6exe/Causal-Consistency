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
class Message_Info:
    def __init__(self):
        self.time = time
        self.centerID = centerID
        self.message
        #(z, message)
'''

HOST = '127.0.0.1'  # Localhost
SERVER_PORT = 58008        # Port for server connections and Port + 1 will be used for client server connections
SERVER_CLIENT_PORT = 0
MASTER_PORT = 58008         # Master port to retrieve other server ports

client_dependency = {}  # {clientaddr: messageID}
messages = {}           # {messageID, message}
pending_writes = {}     # {dependency_messageID, [messageID, message]}
pending_reads = {}      # {dependency_messageID, [messageID, message, client_socket]}
delay_message = {}      # {dependency_messageID, [messageID, message]}

client_sockets_list = []    # List of all slient sockets (including server socket)
client_addresses = {}       # {socket : addr}

self_server_socket = ""     # the socket of the local server
server_sockets_list = []    # [socket]
server_ports = []           # [port]
server_addresses = {}       # {socket : addr}


#Start the server
def start_server():
    global self_server_socket
    global server_sockets_list

    self_server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Create a socket
    self_server_socket.bind((HOST, SERVER_PORT))
    server_sockets_list.append(self_server_socket)
    self_server_socket.listen(4)     #Listen for incoming connections
    self_server_socket.setblocking(False)
    print(f"Server starting on {HOST}:{SERVER_PORT}")

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
    global self_server_socket

    #using select to manage the sockets
    while True:
        readable, writable, exceptional = select.select(server_sockets_list, server_sockets_list, server_sockets_list)
        for current_socket in readable:
            if current_socket == self_server_socket: #establish new connections

                peer_socket, peer_address = self_server_socket.accept()
                peer_socket.setblocking(True)
                server_sockets_list.append(peer_socket)
                #server_addresses[peer_socket] = peer_address
                print(f"Connected by server: {peer_address}")
            else:
                data = current_socket.recv(1024)
                if data:
                    print(f"Received from {current_socket}: {data.decode('utf-8')}")
                else:
                    close_socket(current_socket)
                operation = data.decode('utf-8')
                
                if(operation == "write"):
                    #receives message from other server
                    dependency_messageID = current_socket.recv(1024).decode('utf-8')
                    current_socket.sendall("confirmation".encode('utf-8'))
                    messageID = current_socket.recv(1024).decode('utf-8')
                    current_socket.sendall("confirmation".encode('utf-8'))
                    message = current_socket.recv(1024).decode('utf-8')
                    current_socket.sendall("confirmation".encode('utf-8'))

                    #add to buffer of writes
                    pending_writes[dependency_check] = [messageID, message]

                    #dependency check on the buffer/commit the data
                    dependency_check()

                    print(f"Received replicated write from server: ({messageID},{message}) with dependency on {dependency_messageID}")

#writes to this server
#then broadcasts to other servers
def client_handler():
    global client_sockets_list

    client_server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Create a socket
    client_server_socket.bind((HOST, SERVER_CLIENT_PORT))
    client_sockets_list.append(client_server_socket)
    client_server_socket.listen(4)     #Listen for incoming connections
    client_server_socket.setblocking(False)
    print(f"client server starting on {HOST}:{SERVER_CLIENT_PORT}")

    while True:
        readable, writable, exceptional = select.select(client_sockets_list, client_sockets_list, client_sockets_list)

        for current_socket in readable:
            if current_socket == client_server_socket: 
                #establish new connections
                
                peer_socket, peer_address = client_server_socket.accept()
                peer_socket.setblocking(True)
                client_sockets_list.append(peer_socket)
                client_addresses[peer_socket] = peer_address
                print(f"Connected by client: {peer_address}")

            else:
                #handles client to server commands and broadcasts to other servers

                data = current_socket.recv(1024)
                if data:
                    print(f"Received from {client_addresses[current_socket]}: {data.decode('utf-8')}")

                client_command = data.decode('utf-8')
                if(client_command == "read"):
                    print("Client operation: ", client_command)
                    read(current_socket)
                elif(client_command == "write"):
                    print("Client operation: ", client_command)
                    write(current_socket)

#takes the user write then broadcasts to all other servers
def write(client_socket):
    messageID = client_socket.recv(1024).decode('utf-8')
    message = client_socket.recv(1024).decode('utf-8')
    
    #saving to local server
    dependency_messageID = "None"
    client_addr = client_addresses[client_socket]
    if(client_addr in client_dependency):
        dependency_messageID = client_dependency[client_addr]
    client_dependency[client_addr] = messageID
    messages[messageID] = message

    print(f"Client writes: ({messageID},{message}) with dependency on ({dependency_messageID})")
    print("messages: ", messages)

    #broadcasting to other servers
    for current_socket in server_sockets_list:
        #print("server_addresses: ", server_addresses)
        if(current_socket != self_server_socket):
            print(f"sending message <{messageID},{message}> dependency: <{dependency_messageID}> to {current_socket}")
            current_socket.sendall("write".encode('utf-8'))
            current_socket.sendall(dependency_messageID.encode('utf-8'))
            current_socket.recv(1024)
            current_socket.sendall(messageID.encode('utf-8'))
            current_socket.recv(1024)
            current_socket.sendall(message.encode('utf-8'))
            current_socket.recv(1024)


#updates the dependency list and returns the key to the user
def read(client_socket):
    messageID = client_socket.recv(1024).decode('utf-8')
    if messageID in messages:
        message = messages[messageID]
        client_socket.sendall(message.encode('utf-8'))



#adds all message that can be written
def dependency_check():
    pass

def delay():
    pass

#Close the server and all client connections
def close_server(server_socket):
    print("Closing server and all client connections.")
    for client_socket in client_addresses.values():
        client_socket.close()  #Close each client socket
    server_socket.close()  #Close the server socket
    print("Server closed.")


def close_server_socket():
    pass

#handles closing sockets
def close_client_socket(client_socket, server_socket):
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
    start_server()
    thread2 = threading.Thread(target=client_handler)
    thread3 = threading.Thread(target=server_handler)
    thread2.start()
    thread3.start()