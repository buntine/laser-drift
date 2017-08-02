import socketserver
from multiprocessing import Process

class TCPHandler(socketserver.BaseRequestHandler):
    def handle(self):
        self.data = self.request.recv(1024).strip()
        self.server.q.put(self.data)

class Server(Process):
    def __init__(self, q):
        Process.__init__(self)
        self.q = q

    def run(self):
        server = socketserver.TCPServer(("localhost", 9999), TCPHandler)
        server.q = self.q
        server.serve_forever()
