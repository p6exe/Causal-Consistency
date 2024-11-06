import socket
import select
import threading
import os
import hashlib

HOST = '127.0.0.1'  #The server's hostname or IP address
PORT = 58008        #The port used by the server

file_name = [] #current stores the file name since the file will be stored locally

#established when the user enters the value into the command:
SELFHOST = HOST         #client ip address

files = {}   #{file_name: {chunks}}, file is added when calling register
DEFAULT_CHUNK_SIZE = 4096
threads = []
Selfport = 0

 

#Connects to the server socket
def connect_to_server():
    # Create a socket (TCP/IP)
    close_flag = True # flag for if the program closes
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.connect((HOST, PORT))  # Connect to the server

    print(f"client connecting to server {HOST}:{PORT}")

    # Receive a response from the server
    while(close_flag == True):
        commands = ["close","file list","file location","register","chunk register","download"]
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
        elif(command == "file list"):
            get_list_of_files(server_socket)
        elif(command == "file location"):
            file_name = input("File name: ")
            get_file_location(server_socket, file_name)
        elif(command == "register"):
            file_name = input("File name: ")
            register(server_socket, file_name)
        elif(command == "chunk register"):
            file_name = input("File name: ")
            chunk_register(server_socket, file_name)
        elif(command == "download"):
            file_name = input("File name: ")
            peer_ports = get_file_location(server_socket, file_name)
            if(peer_ports):
                download_from_peers(server_socket, peer_ports, file_name)
        else:
            print("not a valid command: ",commands)


#Send a message to the server
def send(server_socket, message):
    server_socket.sendall(message.encode('utf-8'))  # Send the message encoded


def send_confirmation(client_socket):
    client_socket.sendall("confirm".encode('utf-8'))


#Receive message from server
def recv(server_socket):
    data = server_socket.recv(1024)
    print(f"Received from server: {data.decode('utf-8')}")
    
    if(data.decode('utf-8') == "download chunk"):
        pass
    elif():
        pass
    #send(server_socket, "Message received!")  # Send acknowledgment

#handles closing the client
def close_client(server_socket):
    server_socket.close()
    print("closing")
    

if __name__ == '__main__':
    Selfport = int(input("User port (0 - 65535): " ))
    thread1 = threading.Thread(target=connect_to_server)
    thread2 = threading.Thread(target=start_connection, args = ("localhost", Selfport))
    thread2.start()
    thread1.start()
    


    