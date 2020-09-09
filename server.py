# Server side

import socket
import sys

# User class represents a user in the files sharing network.
class User:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.shared_files = []  # A list of the shared files.

    def get_ip(self):
        return self.ip

    def get_port(self):
        return self.port
    
	# Save the files of the user in the shared files list.
    def save_files(self, files_list_str):
        self.shared_files = files_list_str.split(",")
	
    # Search for a file in the shared files list.
    def search_file(self, file_str):
        files_user_str = ""
        for file in self.shared_files:
            if file.find(file_str) != -1:
                files_user_str = files_user_str + file + " " + self.ip + " " + self.port + ","
        return files_user_str

# Add a user and his files to the files sharing network.	
def add_user_and_files(users_info_list, ip, port, files_list_str):
    user = User(ip, port)
    user.save_files(files_list_str)
    users_info_list.append(user)

# Search for the specified file in the files sharing network and return all the relevant results.
def search_file(users_info_list, file_str):
    files_users_str = ""
    for user in users_info_list:
        files_users_str += user.search_file(file_str)
    return files_users_str

    
def server_side(users_info_list):
    # Create a socket for the server side.
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_ip = '0.0.0.0'
    server_port = sys.argv[1]
    server_socket.bind((server_ip, int(server_port)))
    server_socket.listen(1)
    while True:
        # Accept a new connection request from a client. 
        client_socket, client_address = server_socket.accept()
        client_request = ""
        ending_index = -1
        # The client request ends with '\n'.
        while ending_index == -1:
            ending_index = client_request.find('\n')
            if ending_index == -1:
                client_request += client_socket.recv(4096).decode()
        client_request = client_request[:-1]
        data = client_request.split(" ")
        # Listening mode.
        if data[0] == '1':
            port = data[1]
            files = data[2]
            add_user_and_files(users_info_list, client_address[0], port, files)
        # User mode.
        elif data[0] == '2':
           file_str = data[1]
           if file_str == "":
               client_socket.send("\n".encode())
           else:
               # Search for the specified file in the files sharing network.
               files_and_users = search_file(users_info_list, file_str)
               if len(files_and_users) != 0:
                   files_and_users = files_and_users[:-1]
               files_and_users += "\n"
               # Return all the relevent results to the client.
               client_socket.send(files_and_users.encode())
        client_socket.close()  # Close the current client socket.


def main():
    users_info_list = []  # A list of users in the files sharing network.
    server_side(users_info_list)

	
if __name__ == "__main__":
    main()

