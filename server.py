import socket     # For creating and managing sockets.
import threading  # For handling multiple clients concurrently.
import time
#############################################################################

def handleClient(clientSocket, clientAddress):
    ''' Handles communication with a single client.
        Receives data from the client, processes it,
        and sends a response back.'''

    print('Accepted connection from: {} {}'.\
        format(clientAddress[0], clientAddress[1]))

    while True:
        data = clientSocket.recv(1024)
        # Below if not needed.  clientSocket.recv blocks by default.
        #if not data: break
        print('Received from: {} {}'.format(clientAddress, data.decode()))

        # Process data and send response back to the client
        response = 'Message received!'
        clientSocket.send(response.encode())

        if data.decode() == 'close':
            print('Closing: {}'.format(clientAddress))
            time.sleep(1)
            break

    clientSocket.close()
#############################################################################

def startServer():
    ''' Starts the server and listens for incoming connections.
        Creates a socket object and binds it to a specified host and port.
        Listens for incoming connections. When a client connects, 
        it creates a new thread to handle that client using the 
        handleClient function. '''

    host = '0.0.0.0'  # Listen on all available interfaces
    port = 5000

    serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serverSocket.bind((host, port))
    serverSocket.listen(5)

    print('Server listening on: {} {}'.format(host, port))

    while True:
        clientSocket, clientAddress = serverSocket.accept()
        # Create a new thread to handle the client
        thread = threading.Thread( target=handleClient,
                                   args=( clientSocket,
                                          clientAddress)
                                  )
        thread.start()
#############################################################################

if __name__ == '__main__':
    startServer()
