import socket
import select
import os

'''
The Master is a Server that is connected to all the servers and holds the port of all ports

'''

HOST = '127.0.0.1'  # Localhost
PORT = 58008        # Port 

server_addresses = {}   # {socket : addr}
server_ports = {}       # {socket : ports}
sockets_list = []       # List of all sockets (including master socket)

#Start the server
def start_server():
    
    master_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Create a socket
    master_socket.bind((HOST, PORT))
    master_socket.listen(4)     #Listen for incoming connections
    sockets_list.append(master_socket)
    master_socket.setblocking(False)
    print(f"Master Server starting on {HOST}:{PORT}")

    #using select to manage the sockets
    while True:
        readable, writable, exceptional = select.select(sockets_list, sockets_list, sockets_list)

        for current_socket in readable:
            if current_socket == master_socket: #establish new connections

                server_socket, server_address = master_socket.accept()
                print(f"Connected by {server_address}")
                
                #Set the client socket to non-blocking and add to monitoring list
                server_addresses[server_socket] = server_address
                server_socket.setblocking(True)                                  #doesn't work
                sockets_list.append(server_socket)
            else:
                try:
                    new_server_added(current_socket)
                except ConnectionError as e:
                    #Handle server disconnection
                    close_socket(current_socket)

#handles when new servers are added
def new_server_added(client_socket):
    global server_ports
    
    #send all ports
    length = len(server_ports)
    client_socket.sendall(length.to_bytes(8, byteorder='big'))
    for port in (server_ports.values()):
        client_socket.sendall(port.to_bytes(8, byteorder='big'))
    
    print(f"New Server {server_port}")
    print("list of servers: ", server_ports)

    #recvs the port
    server_port = int.from_bytes(client_socket.recv(1024), byteorder='big')
    server_ports[client_socket] = [server_port]

    

def close_socket(server_socket):
    server_socket.shutdown(socket.SHUT_RDWR)
    server_socket.close()
    print(f"Server {server_addresses[server_socket]} disconnected")
    sockets_list.remove(server_socket)
    del server_ports[server_socket]
    del server_addresses[server_socket]

if __name__ == '__main__':
    start_server()