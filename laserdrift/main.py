import logging
from multiprocessing import Queue, Pipe
from .processes import server, race

class LaserDrift:
    def __init__(self, logfile: str):
        logging.info("Laser Drift Racing System initialization")
    
    def run(self, port=8099, host="localhost", daemon=False, socket="/var/run/lirc/lircd", remote="carrera", players=[0,1]):
        """Start processes and wait for them to return (if ever)."""
        q = Queue()
        parent, child = Pipe(duplex=False)

        self.s = server.Server(q, child, port, host)
        self.r = race.Race(q, parent, players, remote, socket)

        self.s.daemon = daemon
        self.r.daemon = daemon

        self.s.start()
        self.r.start()
        self.r.join()

    def terminate(self):
        """Should be called by implementing program upon receiving OS signal."""
        logging.warn("Laser Drift is terminating.")
        self.s.terminate()
        self.r.terminate()
