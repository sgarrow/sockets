import socket     # For creating and managing sockets.          
import threading  # For handling multiple clients concurrently. 
import time
#############################################################################

def handle_client(client_socket, client_address):
    ''' Handles communication with a single client.
        Receives data from the client, processes it,
        and sends a response back. '''

    print('Accepted connection from: {} {}'.\
        format(client_address[0], client_address[1]))

    while True:
        data = client_socket.recv(1024)
        # Below if not needed.  client_socket.recv blocks by default.
        #if not data: break
        print('Received from: {} {}'.format(client_address, data.decode()))

        # Process data and send response back to the client
        response = 'Message received!'
        client_socket.send(response.encode())

        if data.decode() == 'close':
            print('Closing: {}'.format(client_address))
            time.sleep(1)
            break

    client_socket.close()
#############################################################################

def start_server():
    ''' Starts the server and listens for incoming connections.
        Creates a socket object and binds it to a specified host and port.
        Listens for incoming connections. When a client connects, 
        it creates a new thread to handle that client using the 
        handle_client function. '''

    host = '0.0.0.0'  # Listen on all available interfaces
    port = 5000

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(5)

    print('Server listening on: {} {}'.format(host, port))

    while True:
        client_socket, client_address = server_socket.accept()
        # Create a new thread to handle the client
        thread = threading.Thread( target=handle_client, 
                                   args=( client_socket, 
                                          client_address)
                                  )
        thread.start()
#############################################################################

if __name__ == '__main__':
    start_server()
