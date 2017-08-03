import logging
from multiprocessing import Queue
from processes import server, race

logging.basicConfig(level=logging.INFO)

if __name__ == "__main__":
    logging.info("Carrera Champs Racing System initialization")

    q = Queue()
    s = server.Server(q, port=9999)
    r = race.Race(q, players=[1,3], remote="carrera", socket="/usr/local/var/run/lirc/lircd")

    s.start()
    r.start()
    r.join()
