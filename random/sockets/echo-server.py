import socket

HOST = '127.0.0.1'  # Standard loopback interface address (localhost)
PORT = 65432        # Port to listen on (non-privileged ports are > 1023)

# Create socket object
# socket.AF_INET for ipv4
# socket.SOCK_STREAM for TCP
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    # Assoociate socket with a specific network interface and port
    s.bind((HOST, PORT))
    # Enable server to accept connections
    # Can set a maximum connection count
    # See /proc/sys/net/core/somaxconn for max connections
    s.listen()
    # Block and wait for incoming connection
    # Conn is a socket object representing the connection
    # which is used to communicate with the client; it is
    # separate from the listening socket that the server is
    # using to accept new connections
    conn, addr = s.accept()
    with conn:
        print('Connected by', addr)
        while True:
            # Read data from client
            data = conn.recv(1024)
            if not data:
                break
            # Send data back to client
            conn.sendall(data)