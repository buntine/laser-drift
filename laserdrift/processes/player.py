class Player:
    MAX_SPEED = 16

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
        if s in range(0, Player.MAX_SPEED):
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
