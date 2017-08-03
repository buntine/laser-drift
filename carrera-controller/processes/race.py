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
    def __init__(self, q, players: [int], remote: str, socket: str):
        Process.__init__(self)
        self.q = q
        self.remote = remote
        self.socket = socket
        self.active = False
        self.players = self.__make_players(players)

        logging.info("Race process initialized")

    def run(self):
        sync = "SYNC %s" % self.remote

        with lirc.CommandConnection(socket_path=self.socket) as conn:
            while True:
                if self.active:
                    msg = conn.readline()

                    if sync in msg:
                        for _, p in self.players.items():
                            sleep(0.009)

                            if p.moving():
                                lirc.SendCommand(conn, self.remote, [p.key()]).run()

                while not self.q.empty():
                    self.__handle_message(self.q.get(False))

    def __handle_message(self, msg: str):
        action = msg["message"]

        if re.match(r"start|stop", action):
            self.active = (action == "start")
            logging.info("Race state updated: %s" % action)
        elif re.match(r"speed|lanechange", action):
            data = msg["data"]
            value = data["value"]
            p = self.players.get(data["player"])

            if p:
                f = p.setspeed if action == "speed" else p.setlanechange
                f(value)
                logging.info("Player %d set %s to %s" % (p.nth, action, value))
            else:
                logging.warning("Cannot set %s for player %d" % (action, data["player"]))
        else:
            logging.warning("Unknown command: %s" % action)

    def __make_players(self, players: [Player]):
        p = players.copy()
        p.sort()

        return {n: Player(n) for n in players}
