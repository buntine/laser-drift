import re
import socketserver
from multiprocessing import Process

class TCPHandler(socketserver.BaseRequestHandler):
    def handle(self):
        operation = str(self.request.recv(8).strip(), "utf-8")
        operations = {
            r"start": self.__start,
            r"stop": self.__stop,
            r"p(?P<player>\d)s(?P<speed>\d{1,2})": self.__speed,
            r"p(?P<player>\d)l(?P<status>\d)": self.__lane_change
        }

        for o, f in operations.items():
            match = re.match(o, operation)

            if match:
                message = f(operation, match.groupdict())

                self.server.q.put(message)
                self.request.sendall(b"OK")
                return

        self.request.sendall(b"Invalid operation")

    def __start(self, r, v):
        return {"message": "start", "data": {}}

    def __stop(self, r, v):
        return {"message": "stop", "data": {}}

    def __speed(self, raw, values):
        return {
            "message": "speed",
            "data": {
                "player": int(values["player"]),
                "speed": int(values["speed"]),
                "raw": raw
            }
        }

    def __lane_change(self, raw, values):
        return {
            "message": "lane_change",
            "data": {
                "player": int(values["player"]),
                "enabled": values["status"] == "1",
                "raw": raw
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
