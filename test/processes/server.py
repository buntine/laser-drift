import unittest
from unittest.mock import MagicMock
import laserdrift.processes.server as s

class TestServer(unittest.TestCase):
    def test_pass(self):
        request = MagicMock()
        request.recv = MagicMock(return_value=bytes("p1s4", "utf-8"))
        request.sendall = MagicMock()

        server = MagicMock()
        server.q.put = MagicMock(return_value=None)

        handler = s.TCPHandler(request, None, server)
        handler.handle()

        server.q.put.assert_called_with({"message": "speed", "data": {"player": 1, "value": 4}})

if __name__ == "__main__":
    unittest.main()
