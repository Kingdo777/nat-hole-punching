import threading
import socket
from datetime import datetime


def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    return s.getsockname()[0]


def get_time():
    return str(datetime.now()).split()[1].split(".")[0] + " "


class Accept_Thread(threading.Thread):

    def __init__(self, port, thread_id):
        threading.Thread.__init__(self)
        self.thread_id = thread_id
        self.debug("Initializing ACCEPT thread for port:" + str(port) + "...")
        self.running = False
        self.peer_conn = None
        self.peer_addr = None
        self.return_value = None
        self.debug("Initializing TCP socket...")
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.debug("Setting socket options...")
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        self.debug("Binding socket to " + get_ip() + ":" + str(port))
        self.s.bind((get_ip(), port))
        self.debug("Setting socket to listening settings...")
        self.s.listen(1)
        self.s.settimeout(1)

    def debug(self, a):
        print(get_time() + "ACCEPT THREAD " + str(self.thread_id) + ": " + a)

    def run(self):
        self.debug("Awaiting peer connection...")
        self.running = True
        while self.running:
            try:
                self.peer_conn, self.peer_addr = self.s.accept()
                self.debug("Peer connection received from " + self.peer_addr[0] + ":" + str(
                    self.peer_addr[1]) + ". Exiting thread loop...")
                self.running = False
                # self.return_value = (self.peer_conn, self.peer_addr)
                self.return_value = self.peer_conn
            except socket.timeout:
                continue
        self.debug("Terminating thread...")


class Connect_Thread(threading.Thread):

    def __init__(self, client_private_endpoint, peer_endpoint, thread_id):
        threading.Thread.__init__(self)
        self.thread_id = thread_id
        self.debug("Initializing CONNECT thread for connection between " + client_private_endpoint[0] + ":" + str(
            client_private_endpoint[1]) + " and " + peer_endpoint[0] + ":" + str(peer_endpoint[1]) + "...")
        self.running = False
        self.return_value = None
        self.peer_endpoint = peer_endpoint
        self.debug("Initializing TCP socket")
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.settimeout(1)
        self.debug("Setting socket options...")
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        self.debug("Binding socket to " + client_private_endpoint[0] + ":" + str(client_private_endpoint[1]))
        self.s.bind(client_private_endpoint)

    def debug(self, a):
        print(get_time() + "CONNECT THREAD " + str(self.thread_id) + ": " + a)

    def run(self):
        self.debug(
            "Attempting to connect to peer at " + self.peer_endpoint[0] + ":" + str(self.peer_endpoint[1]) + "...")
        self.running = True
        while self.running:
            try:
                self.s.connect(self.peer_endpoint)
                self.s.settimeout(None)
                self.debug("Sucecssful connection established! Exiting thread loop...")
                self.running = False
                self.return_value = self.s
                print(self.return_value)
            except socket.error:
                continue
        self.debug("Terminating thread...")


def hole_punch(client_public_endpoint, client_private_endpoint, peer_public_endpoint, peer_private_endpoint):
    print(get_time() + "Starting NAT TCP hole punching...")
    # initialize thread objects
    print(get_time() + "Initializing hole punch threads...")
    threads = [Accept_Thread(client_public_endpoint[1], 1),
               Accept_Thread(client_private_endpoint[1], 2),
               Connect_Thread(client_private_endpoint, peer_public_endpoint, 1),
               Connect_Thread(client_private_endpoint, peer_private_endpoint, 2)]
    # start all thread objects
    print(get_time() + "Starting hole punch threads...")
    start = datetime.now()
    for thread in threads: thread.start()
    # wait for one of the threads to produce a return value
    print(get_time() + "Awaiting processed return value from hole punch threads...")
    while not [thread for thread in threads if
               thread.return_value]: pass
    # set running to False for all threads
    print(get_time() + "Return value found. Setting remaining threads to stop...")
    for thread in threads: thread.running = False
    # wait for threads to terminate
    print(get_time() + "Awaiting remaining thread termination...")
    for thread in threads: thread.join()
    # return return value
    print(get_time() + "NAT TCP hole punch complete! Returning completed return values...")
    return [thread.return_value for thread in threads if thread.return_value]
