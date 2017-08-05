from time import sleep
from multiprocessing import Process
import logging
import lirc
import re

class Player:
    def __init__(self, nth: int):
        self.nth = nth
        self.speed = 0
        self.lanechange = False

    def setspeed(self, s: int):
        self.speed = s

    def setlanechange(self, lc: bool):
        self.lanechange = lc

    def moving(self):
        return self.speed > 0

    def key(self):
        return "P%dS%dL%d" % (self.nth, self.speed, 1 if self.lanechange else 0)

class Race(Process):
    """Executes the main game loop. Listens for syncing pulses from Carrera IR tower
       and responds with each players details. Listens for commands from the TCP
       server process."""

    def __init__(self, q, players: [int], remote: str, socket: str):
        Process.__init__(self)
        self.q = q
        self.remote = remote
        self.socket = socket
        self.active = False
        self.players = self.__make_players(players)

        logging.info("Race process initialized")

    def run(self):
        try:
            with lirc.CommandConnection(socket_path=self.socket) as conn:
                while True:
                    if self.active and self.__find_sync(conn):
                        for _, p in self.players.items():
                            if p.moving():
                                sleep(0.009)
                                lirc.SendCommand(conn, self.remote, [p.key()]).run()

                    # Apply state changes as per requests from TCP server.
                    while not self.q.empty():
                        self.__handle_message(self.q.get(False))
        except:
            logging.error("Cannot connect to lirc with socket: %s" % self.socket)

    def __find_sync(self, conn: lirc.client.AbstractConnection):
        """Waits for a blast from the lirc process and returns true if it's
           a syncing signal from the Carrera IR tower."""
        sync = "SYNC %s" % self.remote

        try:
            msg = conn.readline(1)
            return sync in msg
        except:
            logging.warn("Did not receive SYNC from %s, skipping." % self.remote)
            return False

    def __handle_message(self, msg: str):
        """Parse command and attempt to update state of game and/or player."""
        command = msg["message"]

        if re.match(r"start|stop", command):
            self.active = (command == "start")
            logging.info("Race state updated: %s" % command)
        elif re.match(r"speed|lanechange", command):
            data = msg["data"]
            value = data["value"]
            p = self.players.get(data["player"])

            if p:
                f = p.setspeed if command == "speed" else p.setlanechange
                f(value)
                logging.info("Player %d set %s to %s" % (p.nth, command, value))
            else:
                logging.warning("Cannot set %s for player %d" % (command, data["player"]))
        else:
            logging.warning("Unknown command: %s" % command)

    def __make_players(self, players: [Player]):
        p = players.copy()
        p.sort()

        return {n: Player(n) for n in players}
