import socketserver
from multiprocessing import Process

class TCPHandler(socketserver.BaseRequestHandler):
    def handle(self):
        self.data = self.request.recv(8).strip()
        #self.server.q.put(self.data)

class Server(Process):
    def __init__(self, queue, port=8099, host="localhost"):
        Process.__init__(self)
        self.q = queue
        self.port = port
        self.host = host

    def run(self):
        server = socketserver.TCPServer((self.host, self.port), TCPHandler)
        server.q = self.q
        server.serve_forever()
