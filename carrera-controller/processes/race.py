from time import sleep
from multiprocessing import Process
import lirc

class Race(Process):
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
#i = 0
#with lirc.CommandConnection(socket_path="/usr/local/var/run/lirc/lircd") as conn:
#    while True:
#        msg = conn.readline()
#        print(i)
#        i+=1
#
#        sleep(0.010)
#
#        resp = lirc.SendCommand(conn, "carreratower2", ["AA"]).run()
#        print(resp.data)
#
#        sleep(0.010)
#
#        resp = lirc.SendCommand(conn, "carreratower2", "L").run()
#        print(resp.data)
