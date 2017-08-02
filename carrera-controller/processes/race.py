from time import sleep
from multiprocessing import Process
import lirc

class Race(Process):
    def __init__(self, q, remote="", socket="/var/run/lirc/lircd"):
        Process.__init__(self)
        self.q = q
        self.remote = remote
        self.socket = socket
        self.active = False

    def run(self):
        with lirc.CommandConnection(socket_path=self.socket) as conn:
            while True:
                if self.active:
                    msg = conn.readline()

                    sleep(0.009)
                    resp = lirc.SendCommand(conn, self.remote, ["P3S10L1"]).run()

                    sleep(0.009)
                    resp = lirc.SendCommand(conn, self.remote, ["P1S6L0"]).run()

                while not self.q.empty():
                    self.handle_message(self.q.get(False))

    def handle_message(self, msg):
        action = msg["message"]

        if action == "start":
            self.active = True
        elif action == "stop":
            self.active = False
