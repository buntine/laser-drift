from multiprocessing import Queue
from processes import server, race

if __name__ == "__main__":
    q = Queue()

    s = server.Server(q)
    r = race.Race(q)

    s.start()
    r.start()

    r.join()
