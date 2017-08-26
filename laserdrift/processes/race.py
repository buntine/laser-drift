import sched
import time
import logging
import lirc
import re
from multiprocessing import Process, Queue
from collections import OrderedDict
from laserdrift.processes.player import Player

class Race(Process):
    """Executes the main game loop. Listens for syncing pulses from Carrera IR tower
       and responds with each players details. Listens for commands from the TCP
       server process."""

    DELAY = 0.009
    WRITE_TIMEOUT = 0.028
    READ_TIMEOUT = 0.8

    def __init__(self, q: Queue, pipe, players: [int], remote: str, socket: str):
        Process.__init__(self)
        self.q = q
        self.pipe = pipe
        self.remote = remote
        self.socket = socket
        self.conn = None
        self.active = False
        self.players = self.__make_players(players)

        logging.info("Race process initialized")

    def run(self, debug=False):
        try:
            self.conn = self.__lirc_conn();

            while True:
                if self.active and self.__find_sync():
                    schedule = sched.scheduler(time.time, time.sleep)

                    for _, p in self.players.items():
                        if p.moving():
                            schedule.enter(Race.DELAY * p.nth, 1, self.__send, (p,))

                    schedule.run()

                # Apply state changes as per requests from TCP server.
                while not self.q.empty():
                    self.__handle_message(self.q.get(False))

                if debug:
                    break
        except KeyboardInterrupt:
            logging.warn("Terminating Race")
        finally:
            if self.conn:
                self.conn.close()
        
    def __find_sync(self) -> bool:
        """Waits for a blast from the lirc process and returns true if it's
           a syncing signal from the Carrera IR tower."""
        sync = "SYNC %s" % self.remote

        try:
            msg = self.conn.readline(Race.READ_TIMEOUT)
            return sync in msg
        except:
            logging.warn("Did not receive SYNC from %s, skipping." % self.remote)
            return False

    def __handle_message(self, msg: str):
        """Parse command and attempt to update state of game and/or player."""
        command = msg["message"]

        if re.match(r"start|stop", command):
            self.__activate(command)
        elif re.match(r"state", command):
            self.pipe.send({"active": self.active,
                            "players": self.players})
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
        return OrderedDict(map(lambda n: (n, Player(n)), players))

    def __activate(self, command: str):
        self.active = (command == "start")
        logging.info("Race state updated: %s" % command)

    def __send(self, p: Player):
        """Attempt to send command to lirc via the socket."""
        try:
            lirc.SendCommand(self.conn, self.remote, [p.key()]).run(Race.WRITE_TIMEOUT)
        except lirc.client.TimeoutException:
            logging.warn("Player %d send_once to lirc timed out" % p.nth)
        except BrokenPipeError:
            logging.info("Refreshing lirc connection")
            self.conn.close()
            self.conn = self.__lirc_conn()

    def __lirc_conn(self) -> lirc.client.AbstractConnection:
        return lirc.CommandConnection(socket_path=self.socket)
