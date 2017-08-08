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

        self.__handlers = {
            "speed": self.setspeed,
            "incspeed": self.incspeed,
            "lanechange": self.setlanechange,
        }

    def setspeed(self, s: int):
        if s in range(0, 16):
            self.speed = s

    def setlanechange(self, lc: bool):
        self.lanechange = lc

    def incspeed(self, step: int):
        self.setspeed(self.speed + step)

    def moving(self) -> int:
        return self.speed > 0

    def key(self) -> str:
        return "P%dS%dL%d" % (self.nth, self.speed, 1 if self.lanechange else 0)

    def execute(self, command: str, value) -> bool:
        f = self.__handlers.get(command)

        if f:
            f(value)
            return True
        else:
            return False

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
            conn = self.__lirc_conn();

            while True:
                if self.active and self.__find_sync(conn):
                    for _, p in self.players.items():
                        if p.moving():
                            sleep(0.009)

                            try:
                                lirc.SendCommand(conn, self.remote, [p.key()]).run()
                            except BrokenPipeError:
                                logging.info("Refreshing lirc connection")
                                conn.close()
                                conn = self.__lirc_conn()

                # Apply state changes as per requests from TCP server.
                while not self.q.empty():
                    self.__handle_message(self.q.get(False))
        except KeyboardInterrupt:
            logging.warn("Terminating Race")
        finally:
            conn.close()
        
    def __find_sync(self, conn: lirc.client.AbstractConnection) -> bool:
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
            self.__activate(command)
        else:
            data = msg["data"]
            value = data["value"]
            p = self.players.get(data["player"])

            if p:
                if p.execute(command, value):
                    logging.info("Player %d set %s to %s" % (p.nth, command, value))
                else:
                    logging.warning("Unknown command: %s", command)
            else:
                logging.warning("Cannot set %s for player %d" % (command, data["player"]))

    def __make_players(self, players: [Player]) -> hash:
        p = players.copy()
        p.sort()

        return {n: Player(n) for n in players}

    def __activate(self, command: str):
        self.active = (command == "start")
        logging.info("Race state updated: %s" % command)

    def __lirc_conn(self) -> lirc.client.AbstractConnection:
        return lirc.CommandConnection(socket_path=self.socket)
