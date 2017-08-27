import unittest
import laserdrift.processes.race as r
from unittest.mock import MagicMock, Mock, call, patch
from multiprocessing import Queue, Pipe

class TestRace(unittest.TestCase):
    def mock_queue(self, items):
        self.queue = items.copy()
        q = MagicMock()
        q.get = Mock()
        q.get.side_effect = lambda a: self.queue.pop()
        q.empty = Mock()
        q.empty.side_effect = lambda: len(self.queue) == 0

        return q

    def mock_connection(self):
        conn = MagicMock()
        conn.send = MagicMock(return_value=None)

        return conn

    def mock_lirc(self, blast):
        lirc = MagicMock()
        lirc.readline = MagicMock(return_value=blast)
        lirc.close = MagicMock()

        return lirc

    def test_attributes(self):
        (parent, _) = Pipe()
        race = r.Race(Queue(), parent, [1, 2], "remote", "socket")

        self.assertEqual(race.remote, "remote")
        self.assertEqual(race.socket, "socket")
        self.assertTrue(len(race.players), 2)

    def test_player_defaults(self):
        (parent, _) = Pipe()
        race = r.Race(Queue(), parent, [2, 3], "remote", "socket")

        self.assertEqual(race.players[2].nth, 2)
        self.assertEqual(race.players[3].nth, 3)

        self.assertEqual(race.players[2].speed, 0)
        self.assertEqual(race.players[3].speed, 0)

        self.assertEqual(race.players[2].lanechange, False)
        self.assertEqual(race.players[3].lanechange, False)

    def test_requires_lirc(self):
        (parent, _) = Pipe()
        race = r.Race(Queue(), parent, [1, 2], "remote", "socket")

        self.assertRaises(RuntimeError, race.run)

    def test_queue_is_consumed(self):
        items = ["one", {"message": "start", "data": {}}]

        q = self.mock_queue(items)
        c = self.mock_connection()
        race = r.Race(q, c, [1, 2], "remote", "socket")
 
        with patch.object(race, '_Race__lirc_conn', return_value=self.mock_lirc("0000001 SYNC remote")) as lc_method:
            with patch.object(race, '_Race__handle_message', return_value=MagicMock()) as hm_method:
                race.run(True)

                self.assertEqual(hm_method.mock_calls, [call(items[1]), call(items[0])])
                lc_method.assert_called_once()

    def test_state_is_reported(self):
        items = [{"message": "state", "data": {}}]

        q = self.mock_queue(items)
        c = self.mock_connection()
        race = r.Race(q, c, [1, 2], "remote", "socket")
 
        with patch.object(race, '_Race__lirc_conn', return_value=self.mock_lirc("0000001 SYNC remote")) as lc_method:
            race.run(True)

            c.send.assert_called_once()

            # Pull out args to self.pipe.send()
            call = c.send.mock_calls[0]
            _, args, _ = call

            self.assertFalse(args[0]["active"])
            self.assertEqual(len(args[0]["players"]), 2)

if __name__ == "__main__":
    unittest.main()
