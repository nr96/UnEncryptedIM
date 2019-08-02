import socket
import threading
import sys
from termios import tcflush, TCIFLUSH


class Server:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    connections = []

    def __init__(self):
        self.sock.bind(('0.0.0.0', 9999)) # bind to local ip on port 9999
        self.sock.listen(1)  # begin running server
        #print("Server Running...")

    def sender(self, c, a):  # function to handle input from server client
        while True:
            mInput = sys.stdin.readline() # read input from server
            for connection in self.connections:
                connection.send(mInput) # send input from server to clients
            #c.send(mInput)
            #tcflush(sys.stdin, TCIFLUSH)

    def handler(self, c, a):  # function to handle data from clients and their connections
        while True:
            data = c.recv(1024) # handle recieved data
            if not data:
                break
            sys.stdout.write(data) # write out message from client
            for connection in self.connections: # send out message to other clients
                connection.send(data)
            if not data:
                #print(str(a[0]) + ':' + str(a[1]) + " disconnected")
                self.connections.remove(c)
                c.close()
                break

    def run(self):
        while True:
            try:
                try:
                    c, a = self.sock.accept() # accept client connections
                except KeyboardInterrupt:
                    self.sock.close()
                    sys.exit(0)
                sThread = threading.Thread(target=self.handler, args=(c, a))  # create thread to handle server duties
                mThread = threading.Thread(target=self.sender, args=(c, a))  # create thread to handle input from server client
                sThread.daemon = True
                mThread.daemon = True
                sThread.start() # start server handler thread
                mThread.start() # start client handler thread
                self.connections.append(c) # add client to connections list
                print(str(a[0]) + ':' + str(a[1]) + " connected")
            except KeyboardInterrupt:
                self.sock.close()
                sys.exit(0)


class Client:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    def sendMsg(self):  # function to sendMsg to server
        while True:
            cInput = sys.stdin.readline() # read input from client
            #print((cInput))
            self.sock.send(cInput) # send input to server
            #tcflush(sys.stdin, TCIFLUSH)

    def __init__(self, address):
        self.sock.connect((address, 9999))  # connect to server

        cThread = threading.Thread(target=self.sendMsg)  # create thread to handle client input
        cThread.daemon = True
        cThread.start()  # start thread

        while True:  # while loop to handle data from server
            data = self.sock.recv(1024) # receive data from server
            if not data:
                break
            sys.stdout.write(data) # print msg from server


if(len(sys.argv) == 3): # check for args
    try:
        client = Client(sys.argv[2]) # if args, connect to server as cleint
    except KeyboardInterrupt:
        sys.exit(0)
else:
    try:
        server = Server() # if no args, run in server mode
        server.run()
    except KeyboardInterrupt:
        server.close()
        sys.exit(0)
