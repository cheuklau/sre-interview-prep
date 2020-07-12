import socket

HOST = '127.0.0.1'  # The server's hostname or IP address
PORT = 65432        # The port used by the server

# Create socket object
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    # Connect to the server
    s.connect((HOST, PORT))
    # Send data to server
    s.sendall(b'Hello, world')
    # Read server reply
    data = s.recv(1024)

# Print server reply
print('Received', repr(data))