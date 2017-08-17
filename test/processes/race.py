import lirc
import unittest
import laserdrift.processes.race as r
from unittest.mock import MagicMock, patch
from multiprocessing import Queue

class TestRace(unittest.TestCase):
    def setUp(self):
        self.q = Queue()

    def test_attributes(self):
        race = r.Race(self.q, [1, 2], "remote", "socket")

        self.assertEqual(race.remote, "remote")
        self.assertEqual(race.socket, "socket")
        self.assertTrue(len(race.players), 2)
        self.assertTrue(race.players[1].nth, 1)

    def test_requires_lirc(self):
        race = r.Race(self.q, [1, 2], "remote", "socket")

        self.assertRaises(lirc.client.TimeoutException, race.start())
