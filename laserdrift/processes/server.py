import re
import logging
import socketserver
from multiprocessing import Process, Queue

class TCPHandler(socketserver.BaseRequestHandler):
    def handle(self):
        """Parse and validate input. Transform it into valid command for
           the Race process and add it to the queue."""

        command = str(self.request.recv(8).strip(), "utf-8")
        commands = {
            r"^start$": self.__start,
            r"^stop$": self.__stop,
            r"^state$": self.__state,
            r"^p(?P<player>\d)s(?P<speed>\d{1,2})$": self.__speed,
            r"^p(?P<player>\d)s(?P<op>[+-])$": self.__speedinc,
            r"^p(?P<player>\d)l(?P<status>[01])$": self.__lanechange
        }

        for o, f in commands.items():
            match = re.match(o, command)

            if match:
                message = f(match.groupdict())

                if message:
                    self.__send(command, message)

                return

        logging.warning("Unknown command: %s", command)
        self.request.sendall(b"ERR")

    def __send(self, command: str, message: dict):
        """Send command to race process for consumption."""

        self.server.q.put(message)
        self.request.sendall(b"OK")
        logging.info("Server accepted: %s" % command)

    def __state(self, _):
        """Asks race process for current state and returns to requester."""

        self.server.q.put({"message": "state", "data": {}})

        data = self.server.pipe.poll(1)

        if data:
            state = self.server.pipe.recv()
            logging.info("Server accepted: state")
            self.request.sendall(b"test")
        else:
            self.request.sendall(b"ERR")

    def __start(self, _) -> hash:
        return {"message": "start", "data": {}}

    def __stop(self, _) -> hash:
        return {"message": "stop", "data": {}}

    def __speed(self, values: hash) -> hash:
        return {
            "message": "speed",
            "data": {
                "player": int(values["player"]),
                "value": int(values["speed"]),
            }
        }

    def __speedinc(self, values: hash) -> hash:
        return {
            "message": "speedinc",
            "data": {
                "player": int(values["player"]),
                "value": int(1 if values["op"] == "+" else -1),
            }
        }

    def __lanechange(self, values: hash) -> hash:
        return {
            "message": "lanechange",
            "data": {
                "player": int(values["player"]),
                "value": values["status"] == "1",
            }
        }

class Server(Process):
    def __init__(self, queue: Queue, pipe, port: int, host: str):
        Process.__init__(self)
        self.q = queue
        self.pipe = pipe
        self.port = port
        self.host = host

    def run(self):
        """Starts a TCP server that listens for commands and funnels them
           safelty to the Race process for execution."""

        try:
            server = socketserver.TCPServer((self.host, self.port), TCPHandler)
            server.q = self.q
            server.pipe = self.pipe

            logging.info("TCP server process initialized")

            server.serve_forever()
        except OSError:
            logging.error("Cannot start TCP server on %s:%d" % (self.host, self.port))
        except KeyboardInterrupt:
            logging.warn("Terminating server")
            server.shutdown()
