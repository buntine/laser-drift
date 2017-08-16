import unittest
from unittest.mock import MagicMock
import laserdrift.processes.server as s

class TestServer(unittest.TestCase):
    def mock_request(self, response: str) -> MagicMock:
        req = MagicMock()
        req.recv = MagicMock(return_value=bytes(response, "utf-8"))
        req.sendall = MagicMock()

        return req

    def mock_server(self) -> MagicMock:
        server = MagicMock()
        server.q.put = MagicMock(return_value=None)

        return server

    def test_pass(self):
        request = self.mock_request("p1s4")
        server = self.mock_server()
       
        handler = s.TCPHandler(request, None, server)
        handler.handle()

        server.q.put.assert_called_with({"message": "speed", "data": {"player": 1, "value": 4}})
        request.sendall.assert_called_with(b"OK")

if __name__ == "__main__":
    unittest.main()
