import re
import logging
import socketserver
from multiprocessing import Process

class TCPHandler(socketserver.BaseRequestHandler):
    def handle(self):
        operation = str(self.request.recv(8).strip(), "utf-8")
        operations = {
            r"start": self.__start,
            r"stop": self.__stop,
            r"p(?P<player>\d)s(?P<speed>\d{1,2})": self.__speed,
            r"p(?P<player>\d)l(?P<status>\d)": self.__lanechange
        }

        for o, f in operations.items():
            match = re.match(o, operation)

            if match:
                message = f(operation, match.groupdict())

                self.server.q.put(message)
                self.request.sendall(b"OK")
                logging.info("Server accepted: %s" % operation)
                return

        logging.warning("Unknown command: %s", operation)
        self.request.sendall(b"Invalid operation")

    def __start(self, v):
        return {"message": "start", "data": {}}

    def __stop(self, v):
        return {"message": "stop", "data": {}}

    def __speed(self, values):
        return {
            "message": "speed",
            "data": {
                "player": int(values["player"]),
                "value": int(values["speed"]),
            }
        }

    def __lanechange(self, values):
        return {
            "message": "lanechange",
            "data": {
                "player": int(values["player"]),
                "value": values["status"] == "1",
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

        logging.info("TCP Server process initialized")

        server.serve_forever()
