from multiprocessing import Process, Queue
from time import sleep
import socketserver

class TCPHandler(socketserver.BaseRequestHandler):
    def handle(self):
        self.data = self.request.recv(1024).strip()
        self.server.q.put(self.data)

class ServerProcess(Process):
    def __init__(self, q):
        Process.__init__(self)
        self.q = q

    def run(self):
        server = socketserver.TCPServer(("localhost", 9999), TCPHandler)
        server.q = self.q
        server.serve_forever()

class RaceProcess(Process):
    def __init__(self, q):
        Process.__init__(self)
        self.q = q
        self.data = "Hello"

    def run(self):
        while True:
            while not self.q.empty():
                self.data = self.q.get(False)

            print(self.data)
            sleep(0.2)

if __name__ == "__main__":
    q = Queue()

    s = ServerProcess(q)
    r = RaceProcess(q)

    s.start()
    r.start()

    r.join()
