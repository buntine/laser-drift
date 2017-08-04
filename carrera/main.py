import logging
from multiprocessing import Queue
from .processes import server, race

class Carrera:
    def __init__(self):
        logging.basicConfig(level=logging.INFO)
    
    def run(self, port=8099, host="localhost", socket="/var/run/lirc/lircd", remote="carrera", players=[0,1]):
        """Start processes and wait for them to return (if ever)"""
        logging.info("Carrera Champs Racing System initialization")

        q = Queue()
        s = server.Server(q, port, host)
        r = race.Race(q, players, remote, socket)

        s.start()
        r.start()
        r.join()
