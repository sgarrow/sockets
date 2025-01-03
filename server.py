'''
This file contains three functions.

Function startServer:
Starts when "python3 server.py" is entered on the command line. Listens
for incoming connections in an infinite loop. When a client connects, it 
creates a new thread to handle it via the handleClient function.  When a
client connects startServer spawns a new thread to handle that client.  The
server can/will be shutdown when a client issues ta "ks" (kill server) cmd.
The ks command (1) sends a message to all clients (including the the one sent
the cmnd) that the server is shutting down so that the client will exit 
gracefully, (2) close all client sockets and then (3) exit it's infinite loop.

Function handleClient:
Each handleClient is it's own thread.  Multiple clientHandler threads may be
active simultaneously.  Receives data from the client, processes it, and
sends a response back to the client.

A client can be run (1) on the the same machine as the server is running or 
(2) on remote machine via an SSH connection (PC or phone (via the Terminus 
App)) or (3) on a remote machine directly (not on an SSH connection).

Function listThreads:
Runs in it's own thread and every 30 seconds.  It prints all the currently 
running threads in the server's terminal window.  It's just a debug function.
Similar functionality is available to he client via the gat cmd.
'''

import socket           # For creating and managing sockets.
import threading        # For handling multiple clients concurrently.
import queue            # For Killing Server.
import time             # For Killing Server and listThreads.
import cmdVectors as cv # Contains vectors to "worker" functions.

openSocketsLst = []     # Needed for processing the "ks" command only.
#############################################################################

def listThreads():
    while True:
        time.sleep(30)
        print(' Active Threads: ')
        for t in threading.enumerate():
            print('   {}'.format(t.name))
        print(' ##################')
        print(' Open Sockets: ')
        for openS in openSocketsLst:
            print('   {}'.format(openS['ca']))
        print(' ##################')
#############################################################################

def handleClient(clientSocket, clientAddress, client2ServerCmdQ):
    global openSocketsLst
    print(' Accepted connection from: {}'.format(clientAddress))
    openSocketsLst.append({'cs':clientSocket,'ca':clientAddress})
    clientSocket.settimeout(3.0) # Sets the .recv timeout - ks processing.

    # The while condition is made false by the close and ks command.
    while {'cs':clientSocket,'ca':clientAddress} in openSocketsLst:

        # Recieve a message from the client.
        try: # In case user closed client window (x) instead of by close cmd.
            data = clientSocket.recv(1024)
        except ConnectionResetError: # Windows throws this on (x).
            print(' handleClient {} ConnectRstErr except in s.recv'.format(clientAddress))
            # Breaks the loop. handler/thread stops. Connection closed.
            openSocketsLst.remove({'cs':clientSocket,'ca':clientAddress})
            break
        except socket.timeout: # Can't block on recv - won't be able to break
            continue           # loop if another client has issued a ks cmd. 

        # Getting here means a command has been received.
        print('*********************************')
        print(' handleClient {} received: {}'.format(clientAddress, data.decode()))

        # Process a "close" message and send response back to the local client.
        if data.decode() == 'close':
            rspStr = ' handleClient {} set loop break RE: close'.format(clientAddress)
            clientSocket.send(rspStr.encode()) # sends all even if >1024.
            time.sleep(1) # Required so .send happens before socket closed.
            print(rspStr)
            # Breaks the loop, connection closes and thread stops. 
            openSocketsLst.remove({'cs':clientSocket,'ca':clientAddress})

        # Process a "ks" message and send response back to other client(s).
        elif data.decode() == 'ks':
            # Client sending ks has to be terminated first, I don't know why.
            rspStr = ' handleClient {} set loop break for self RE: ks'.format(clientAddress)
            clientSocket.send(rspStr.encode()) # sends all even if > 1024.
            time.sleep(1) # Required so .send happens before socket closed.
            print(rspStr)
            # Breaks the ALL loops, ALL connections close and ALL thread stops.
            for el in openSocketsLst:
                if el['ca'] != clientAddress:
                    rspStr = ' handleClient {} set loop break for {} RE: ks'.\
                        format(clientAddress, el['ca'])
                    el['cs'].send(rspStr.encode()) # sends all even if > 1024.
                    time.sleep(1) # Required so .send happens before socket closed.
                    print(rspStr)
            openSocketsLst = []
            client2ServerCmdQ.put('ks')

        # Process a "standard" message and send response back to the client.
        else:
            response = cv.vector(data.decode())
            try: # In case user closed client window (x) instead of by close cmd.
                clientSocket.send(response.encode())
            except BrokenPipeError:      # RPi throws this on (x).
                print(' handleClient {} BrokePipeErr except in s.send'.format(clientAddress))
                # Breaks the loop. handler/thread stops. Connection closed.
                openSocketsLst.remove({'cs':clientSocket,'ca':clientAddress})

    print(' handleClient {} closing socket and breaking loop'.format(clientAddress))
    clientSocket.close()
#############################################################################

def printSocketInfo(sSocket):
    sndBufSize = sSocket.getsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF)
    rcvBufSize = sSocket.getsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF)
    print('sndBufSize',sndBufSize) # 64K
    print('rcvBufSize',rcvBufSize) # 64K
#############################################################################

def startServer():
    host = '0.0.0.0'  # Listen on all available interfaces
    port = 4242

    serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serverSocket.bind((host, port))
    serverSocket.listen(5)
    serverSocket.settimeout(3.0) # Sets the .accept timeout - ks processing.

    clientToServerCmdQ = queue.Queue() # So client can tell server to stop.

    thread = threading.Thread( target = listThreads,
                               name   = 'listThreads',
                               daemon = True )
    thread.start()

    printSocketInfo(serverSocket)

    print('Server listening on: {} {}'.format(host, port))
    while True:

        # See if any client has requested the server to halt (ks command).
        try:
            cmd = clientToServerCmdQ.get(timeout=.1)
        except queue.Empty:
            pass
        else:
            if cmd == 'ks':
                print('Server breaking in 6 sec.')
                time.sleep(6)
                break


        # See if any new clients are trying to connect.
        try:
            clientSocket, clientAddress = serverSocket.accept()
        except socket.timeout: # Can't block on accept - won't be able to
            continue           # break loop if a client has issued a ks cmd.
        else:
            # Yes, create a new thread to handle the new client.
            print('Starting a new client handler thread.')

            cThrd = threading.Thread( target=handleClient,

                                      args = ( clientSocket,
                                               clientAddress,
                                               clientToServerCmdQ ),

                                      name =   'handleClient-{}'.\
                                               format(clientAddress) )
            cThrd.start()
    print('Server breaking.')
#############################################################################

if __name__ == '__main__':
    #sp.sprinkler('rp')
    startServer()
