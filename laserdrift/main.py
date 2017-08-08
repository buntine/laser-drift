import logging
from multiprocessing import Queue
from .processes import server, race

class LaserDrift:
    def __init__(self, logfile: str):
        logging.basicConfig(filename=logfile, level=logging.INFO)
        logging.info("Laser Drift Racing System initialization")
    
    def run(self, port=8099, host="localhost", socket="/var/run/lirc/lircd", remote="carrera", players=[0,1]):
        """Start processes and wait for them to return (if ever)."""
        q = Queue()
        self.s = server.Server(q, port, host)
        self.r = race.Race(q, players, remote, socket)

        self.s.daemon = True
        self.r.daemon = True

        self.s.start()
        self.r.start()
        self.r.join()

    def terminate(self):
        """Should be called by implementing program upon receiving OS signal."""
        logging.warn("Laser Drift is terminating.")
        self.s.terminate()
        self.r.terminate()
