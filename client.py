# Client side

import socket
import sys
import os
from collections import OrderedDict


# Scan all the files in the current directory and return a concatenation of their names.
def scan_files_in_dir():
    files_list_str = ""
    entries = os.scandir()
    for entry in entries:
        # If the current entry is a file - concatenate it to the file names.
        if entry.is_file():
            files_list_str = files_list_str + entry.name + ","
    # Cut the last comma and return the file names.
    files_list_str = files_list_str[:-1]
    return files_list_str


# Connect the listener client to the server.
def connect_listener_client_to_server():
    # Create a socket between the listener client and the server.
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_ip = sys.argv[2]  # The IP of the server.
    server_port = sys.argv[3]  # The port of the server.
    listening_port = sys.argv[4]  # The listening port of the listener client.
    server_socket.connect((server_ip, int(server_port)))  # Connect to the socket.
    files_list_str = scan_files_in_dir()
    msg = "1 " + listening_port + " " + files_list_str + "\n"
    server_socket.send(msg.encode())
    server_socket.close()  # Close the socket.

	
# The listener client serves as a server - other clients can download files from it.
def listener_client_as_a_server():
    # Create the socket of the listener client that will serve as a server.
    listening_client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listening_client_ip = '0.0.0.0'  # The IP of the listener client.
    listening_client_port = sys.argv[4]  # The listening port of the listener client.
    # Bind the socket to the IP & port.
    listening_client_socket.bind((listening_client_ip, int(listening_client_port)))
    # Put the socket into listening mode and handle one client at a time.
    listening_client_socket.listen(1)
    while True:
        # Accept a new user-mode client in a separate socket.
        client_socket, client_address = listening_client_socket.accept()
        # Get the required file name from the user-mode client.
        file_name = client_socket.recv(1024)
        f = open(file_name, 'rb')  # Open the file in read mode.
        # Read the file in chunks and send it to the user-mode client.
        chunk_size = 4096
        temp = f.read(chunk_size)
        while temp:
            client_socket.send(temp)
            temp = f.read(chunk_size)
        # An empty message indicates that there is no more what to read.
        client_socket.send("".encode())
        f.close()  # Close the file.
        client_socket.close()  # Close the socket.


# Client in listening mode.
def listening_mode():
    # The listener client connects to the server to share his files with it.
    connect_listener_client_to_server()
    # At this point on, the listener client will serve as a server.
    listener_client_as_a_server()


# Search a file for the user.
# Param s: the socket between the user-mode client and the server.
def search_file(s):
    # Get the file name or part of the file name from the user.
    msg = input('Search: ')
    msg = "2 " + msg + "\n"
    # Send the request to the server.
    s.send(msg.encode())
    # Get all the relevant information from the server. Read the data in chunks.
    chunk_size = 4096
    files_and_users = s.recv(chunk_size).decode()
    ending_index = files_and_users.find('\n')
    while ending_index == -1:
        files_and_users += s.recv(chunk_size).decode()
        ending_index = files_and_users.find('\n')
    files_and_users = files_and_users[:-1]  # Cut the last \n.
    return files_and_users

	
# Sort the files in a lexicographic order and display them.
def sort_files_lexicographically(files_and_users):
    # The keys of the dictionary are file names.
    # The values are lists of tuples - (ip, port) of the clients that have this file.
    dictionary = dict()
    list_of_files_details = files_and_users.split(",")
    for entry in list_of_files_details:
        details = entry.split(" ")
        if details[0] not in dictionary:
            dictionary[details[0]] = []
        dictionary[details[0]].append((details[1], details[2]))
    # Sort the files in a lexicographic order.
    ordered_dictionary = OrderedDict(sorted(dictionary.items(), key=lambda t: t[0]))
    current_index = 1
    chosen_file_name = ""
    clients_list = []
    # Display the files that can be downloaded.
    for key in ordered_dictionary:
        for client_details in ordered_dictionary[key]:
            print(str(current_index) + " " + key)
            clients_list.append((key, client_details))
            current_index += 1
    return clients_list

# Return True if the search format is valid, otherwise - return False.
def is_a_valid_search(files_and_users, chosen_client_index, len_clients_list):
    if files_and_users != "" and chosen_client_index.isnumeric() and int(chosen_client_index) > 0 and int(chosen_client_index) <= len_clients_list:
        return True
    else:
        return False

# The user chooses a file to download.
def choose_file(files_and_users, clients_list):
    chosen_client_index = input('Choose: ')
    if is_a_valid_search(files_and_users, chosen_client_index, len(clients_list)):
        chosen_client_details = clients_list[int(chosen_client_index) - 1][1]
        # Create a socket between the user-mode client and the listener client.
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Connect to the socket.
        client_socket.connect((chosen_client_details[0], int(chosen_client_details[1])))
        # Find the desired file name.
        chosen_file_name = clients_list[int(chosen_client_index) - 1][0]
        file_to_write = open(chosen_file_name, 'wb')  # Open the file in write mode.
        # Read the content of the file in chunks.
        client_socket.send(chosen_file_name.encode())
        file_to_read = "".encode()
        chunk_size = 4096
        temp = client_socket.recv(chunk_size)
        while temp:
            file_to_read += temp
            temp = client_socket.recv(chunk_size)
        file_to_write.write(file_to_read)  # Write the content in the file.
        file_to_write.close()  # Close the file.
        client_socket.close()  # Close the socket.

# Client in user mode.
def user_mode():
    server_ip = sys.argv[2]  # The IP of the server.
    server_port = sys.argv[3]  # The port of the server.
    while True:
        # Create a socket between the user-mode client and the server.
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((server_ip, int(server_port)))  # Connect to the server.
        # Search a file and get the relevant information about it.
        files_and_users = search_file(s)
        clients_list = []
        if files_and_users != "":
            # Sort the files in lexicographic order and display them to the user.
            clients_list = sort_files_lexicographically(files_and_users)
        s.close()  # Close the socket.
        choose_file(files_and_users, clients_list)  # Choose a file to download.


def main():
    # Client in listening mode.
    if sys.argv[1] == '0':
        listening_mode()
    # Client in user mode.
    elif sys.argv[1] == '1':
        user_mode()
    # Else - invalid input, ignore.

	
if __name__ == "__main__":
    main()

