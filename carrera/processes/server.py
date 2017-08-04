import re
import logging
import socketserver
from multiprocessing import Process

class TCPHandler(socketserver.BaseRequestHandler):
    def handle(self):
        """Parse and validate input. Transform it into valid command for
           the Race process and add it to the queue."""
        command = str(self.request.recv(8).strip(), "utf-8")
        commands = {
            r"start": self.__start,
            r"stop": self.__stop,
            r"p(?P<player>\d)s(?P<speed>\d{1,2})": self.__speed,
            r"p(?P<player>\d)l(?P<status>\d)": self.__lanechange
        }

        for o, f in commands.items():
            match = re.match(o, command)

            if match:
                message = f(command, match.groupdict())

                self.server.q.put(message)
                self.request.sendall(b"OK")
                logging.info("Server accepted: %s" % command)
                return

        logging.warning("Unknown command: %s", command)
        self.request.sendall(b"Invalid command")

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
    def __init__(self, queue, port: int, host: str):
        Process.__init__(self)
        self.q = queue
        self.port = port
        self.host = host

    def run(self):
        """Starts a TCP server that listens for commands and funnels them
           safelty to the Race process for execution."""
        server = socketserver.TCPServer((self.host, self.port), TCPHandler)
        server.q = self.q

        logging.info("TCP Server process initialized")

        server.serve_forever()
