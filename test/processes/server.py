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

    def test_invalid_a(self):
        request = self.mock_request("banana")
        server = self.mock_server()
       
        handler = s.TCPHandler(request, None, server)
        handler.handle()

        server.q.put.assert_not_called()
        request.sendall.assert_called_with(b"ERR")

    def test_invalid_b(self):
        request = self.mock_request("p10s999")
        server = self.mock_server()
       
        handler = s.TCPHandler(request, None, server)
        handler.handle()

        server.q.put.assert_not_called()
        request.sendall.assert_called_with(b"ERR")

    def test_start(self):
        request = self.mock_request("start")
        server = self.mock_server()
       
        handler = s.TCPHandler(request, None, server)
        handler.handle()

        server.q.put.assert_called_with({"message": "start", "data": {}})
        request.sendall.assert_called_with(b"OK")

    def test_stop(self):
        request = self.mock_request("stop")
        server = self.mock_server()
       
        handler = s.TCPHandler(request, None, server)
        handler.handle()

        server.q.put.assert_called_with({"message": "stop", "data": {}})
        request.sendall.assert_called_with(b"OK")

if __name__ == "__main__":
    unittest.main()
