import unittest
from unittest.mock import MagicMock
import laserdrift.processes.race as r

class TestServer(unittest.TestCase):
    def setUp(self):
        self.q = self.mock_queue()

    def mock_queue(self) -> MagicMock:
        queue = MagicMock()
        queue.get = MagicMock(return_value={})
        queue.empty = MagicMock(return_value=True)

        return queue

    def test_attributes(self):
        race = r.Race(self.q, [1, 2], "remote", "socket")

        self.assertEqual(race.remote, "remote")
        self.assertEqual(race.socket, "socket")
        self.assertTrue(len(race.players), 2)
        self.assertTrue(race.players[1].nth, 1)
