from time import sleep
from multiprocessing import Process
import lirc

class Race(Process):
    def __init__(self, q):
        Process.__init__(self)
        self.q = q
        self.active = False

    def run(self):
        with lirc.CommandConnection(socket_path="/usr/local/var/run/lirc/lircd") as conn:
            while True:
                if self.active:
                    msg = conn.readline()

                    sleep(0.010)
                    resp = lirc.SendCommand(conn, "carreratower2", ["AA"]).run()

                    sleep(0.010)
                    resp = lirc.SendCommand(conn, "carreratower2", "L").run()

                while not self.q.empty():
                    self.handle_message(self.q.get(False))

    def handle_message(self, msg):
        action = msg["message"]

        if action == "start":
            self.active = True
        elif action == "stop":
            self.active = False
