import unittest
import laserdrift.processes.player as p

class TestPlayer(unittest.TestCase):
    def test_default_key(self):
        p1 = p.Player(1)
        p3 = p.Player(3)

        self.assertEqual("P1S0L0", p1.key())
        self.assertEqual("P3S0L0", p3.key())

    def test_key(self):
        p1 = p.Player(1)
        p3 = p.Player(3)

        p1.setspeed(5)
        p3.setspeed(13)

        p1.setlanechange(True)

        self.assertEqual("P1S5L1", p1.key())
        self.assertEqual("P3S13L0", p3.key())

        p1.setlanechange(False)
        p3.setlanechange(True)

        p1.setspeed(15)

        self.assertEqual("P1S15L0", p1.key())
        self.assertEqual("P3S13L1", p3.key())

    def test_nth(self):
        p1 = p.Player(1)

        self.assertEqual(p1.nth, 1)

    def test_setters(self):
        p1 = p.Player(2)

        self.assertEqual(p1.speed, 0)
        self.assertEqual(p1.lanechange, False)

        p1.setspeed(5)
        p1.setlanechange(True)

        self.assertEqual(p1.speed, 5)
        self.assertEqual(p1.lanechange, True)

    def test_incs(self):
        p1 = p.Player(1)

        p1.incspeed(1)

        self.assertEqual(p1.speed, 1)

        p1.incspeed(1)
        p1.incspeed(-1)

        self.assertEqual(p1.speed, 1)

        p1.incspeed(1)

        self.assertEqual(p1.speed, 2)

    def test_execute(self):
        p1 = p.Player(3)

        v = p1.execute("speed", 4)

        self.assertTrue(v)
        self.assertEqual(p1.speed, 4)

        v = p1.execute("speed", 6)

        self.assertTrue(v)
        self.assertEqual(p1.speed, 6)

        v = p1.execute("incspeed", 1)

        self.assertTrue(v)
        self.assertEqual(p1.speed, 7)

        self.assertEqual(p1.lanechange, False)

        v = p1.execute("lanechange", True)

        self.assertTrue(v)
        self.assertEqual(p1.lanechange, True)

    def test_invalid_execute(self):
        p1 = p.Player(0)

        v = p1.execute("cheese", 4)

        self.assertFalse(v)
