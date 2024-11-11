import socket
import select
import os

'''
The Master is a Server that is connected to all the servers and holds the port of all ports

'''
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
        readable, writable, exceptional = select.select(sockets_list, sockets_list, sockets_list)
        pass


HOST = '127.0.0.1'  # Localhost
PORT = 58008        # Port 