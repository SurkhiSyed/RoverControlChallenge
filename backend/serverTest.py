#Not important file, used to test the main.py file if proper packets were recieved

import socket
import json

# Create a socket object
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(("0.0.0.0", 5000))  # Bind to any available network interface on port 5000
server_socket.listen(5)  # Start listening for incoming connections

print("Server is listening...")

# Wait for client connections
client_socket, address = server_socket.accept()
print(f"Connection established with {address}")

while True:
    try:
        # Receive data from the client
        data = client_socket.recv(1024)  # Buffer size of 1024 bytes
        if not data:
            break
        data = json.loads(data.decode('utf-8'))
        
        # Print each value on a new line
        for value in data.values():
            print(value)

    except json.JSONDecodeError as e:
        print("Error decoding JSON:", e)
        break

# Close the connection
client_socket.close()
server_socket.close()
