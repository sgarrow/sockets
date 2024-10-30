import socket
import time
#############################################################################

if __name__ == '__main__':

    # Each client will connect to the server with a new address.
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Replace with the server's address if needed.
    client_socket.connect(('localhost', 5000))

    for ii in range(10):

        time.sleep(1)

        message = 'Client 2 command number {}'.format(ii)

        if ii == 7:
            message = 'close'

        client_socket.send(message.encode())

        response = client_socket.recv(1024)
        print('2 Response from server: {}'.format(response.decode()))

        if message == 'close':
            break

    client_socket.close()
