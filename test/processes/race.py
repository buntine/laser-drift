import unittest
import laserdrift.processes.race as r

class TestPlayer(unittest.TestCase):
    def test_default_key(self):
        p1 = r.Player(1)
        p3 = r.Player(3)

        self.assertEqual("P1S0L0", p1.key())
        self.assertEqual("P3S0L0", p3.key())

    def test_key(self):
        p1 = r.Player(1)
        p3 = r.Player(3)

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
        p = r.Player(1)

        self.assertEqual(p.nth, 1)

    def test_setters(self):
        p = r.Player(2)

        self.assertEqual(p.speed, 0)
        self.assertEqual(p.lanechange, False)

        p.setspeed(5)
        p.setlanechange(True)

        self.assertEqual(p.speed, 5)
        self.assertEqual(p.lanechange, True)

    def test_incs(self):
        p = r.Player(1)

        p.incspeed(1)

        self.assertEqual(p.speed, 1)

        p.incspeed(1)
        p.incspeed(-1)

        self.assertEqual(p.speed, 1)

        p.incspeed(1)

        self.assertEqual(p.speed, 2)

    def test_execute(self):
        p = r.Player(3)

        v = p.execute("speed", 4)

        self.assertTrue(v)
        self.assertEqual(p.speed, 4)

        v = p.execute("speed", 6)

        self.assertTrue(v)
        self.assertEqual(p.speed, 6)

        v = p.execute("incspeed", 1)

        self.assertTrue(v)
        self.assertEqual(p.speed, 7)

        self.assertEqual(p.lanechange, False)

        v = p.execute("lanechange", True)

        self.assertTrue(v)
        self.assertEqual(p.lanechange, True)

    def test_invalid_execute(self):
        p = r.Player(0)

        v = p.execute("cheese", 4)

        self.assertFalse(v)
