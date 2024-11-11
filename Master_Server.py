import socket
import select
import os

'''
The Master is a Server that is connected to all the servers and holds the port of all ports

'''

HOST = '127.0.0.1'  # Localhost
PORT = 58008        # Port 

#Start the server
def start_server():
    
    sockets_list = []   # List of all sockets (including server socket)
    socket_addr = {} 

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Create a socket
    server_socket.bind((HOST, PORT))
    server_socket.listen(4)     #Listen for incoming connections
    sockets_list.append(server_socket)
    server_socket.setblocking(False)
    print(f"Server starting on {HOST}:{Selfport}")

    #using select to manage the sockets
    while True:
        for current_socket in readable:
            if current_socket == server_socket: #establish new connections

                client_socket, client_address = server_socket.accept()
                print(f"Connected by {client_address}")
                
                #Set the client socket to non-blocking and add to monitoring list
                client_addresses[client_socket] = client_address
                client_socket.setblocking(True)                                  #doesn't work
                sockets_list.append(client_socket)

#handles when new servers are added
def new_server_added():
    pass


HOST = '127.0.0.1'  # Localhost
PORT = 58008        # Port 