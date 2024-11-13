import socket
import select
import threading
import os
import hashlib

HOST = '127.0.0.1'  #The server's hostname or IP address

file_name = [] #current stores the file name since the file will be stored locally

#established when the user enters the value into the command:

files = {}   #{file_name: {chunks}}, file is added when calling register


#Connects to the server socket
def connect_to_server():
    # Create a socket (TCP/IP)
    close_flag = True # flag for if the program closes
    Server_port = int(input("Server port (0 - 65535): " ))                          #################
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.connect((HOST, Server_port))  # Connect to the server

    print(f"client connecting to server {HOST}:{Server_port}")

    # Receive a response from the server
    while(close_flag == True):
        commands = ["read", "write"]
        print("Commands: ",commands)
        command = input("command: ").lower()

        if(command == "write"): 
            write(server_socket)
        elif(command == "read"):
            read(server_socket)
        else:
            print("not a valid command: ",commands)


#Send a message to the server
def write(server_socket, message):
    server_socket.sendall(message.encode('utf-8'))  # Send the message encoded

#Receive message from server
def read(server_socket):
    command = server_socket.recv(1024).decode('utf-8')
    print(f"Received from server: {command}")
    #send(server_socket, "Message received!")  # Send acknowledgment

def send_confirmation(client_socket):
    client_socket.sendall("confirm".encode('utf-8'))

#handles closing the client
def close_client(server_socket):
    server_socket.close()
    print("closing")
    

if __name__ == '__main__':
    connect_to_server()
    


    