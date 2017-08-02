import re
import socketserver
from multiprocessing import Process

class TCPHandler(socketserver.BaseRequestHandler):
    def handle(self):
        operation = str(self.request.recv(8).strip(), "utf-8")
        operations = {
            "start": self.__start,
            "stop": self.__stop,
            "p\ds\d{1,2}": self.__speed,
            "p\dl\d": self.__lane_change
        }

        for o, f in operations.items():
            if re.match(o, operation):
                message = f(operation)

                self.server.q.put(message)
                self.request.sendall(b"OK")
                return

        self.request.sendall(b"Invalid operation")

    def __start(self, _):
        return {"message": "start", "data": {}}

    def __stop(self, _):
        return {"message": "stop", "data": {}}

    def __speed(self, _):
        return {
            "message": "speed",
            "data": {
                "player": 1,
                "speed": 6
            }
        }

    def __lane_change(self, _):
        return {
            "message": "lane_change",
            "data": {
                "player": 1,
                "enabled": False
            }
        }

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
