import unittest
from unittest.mock import MagicMock
import laserdrift.processes.server as s

class TestServer(unittest.TestCase):
    def setUp(self):
        self.server = self.mock_server()

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
       
        handler = s.TCPHandler(request, None, self.server)
        handler.handle()

        self.server.q.put.assert_not_called()
        request.sendall.assert_called_with(b"ERR")

    def test_invalid_b(self):
        request = self.mock_request("p10s999")
       
        handler = s.TCPHandler(request, None, self.server)
        handler.handle()

        self.server.q.put.assert_not_called()
        request.sendall.assert_called_with(b"ERR")

    def test_start(self):
        request = self.mock_request("start")
       
        handler = s.TCPHandler(request, None, self.server)
        handler.handle()

        self.server.q.put.assert_called_with({"message": "start", "data": {}})
        request.sendall.assert_called_with(b"OK")

    def test_stop(self):
        request = self.mock_request("stop")
       
        handler = s.TCPHandler(request, None, self.server)
        handler.handle()

        self.server.q.put.assert_called_with({"message": "stop", "data": {}})
        request.sendall.assert_called_with(b"OK")

    def test_speed_a(self):
        request = self.mock_request("p1s5")
       
        handler = s.TCPHandler(request, None, self.server)
        handler.handle()

        self.server.q.put.assert_called_with({
            "message": "speed",
            "data": {
                "player": 1,
                "value": 5,
            }
        })
        request.sendall.assert_called_with(b"OK")

    def test_speed_b(self):
        request = self.mock_request("p1s13")
       
        handler = s.TCPHandler(request, None, self.server)
        handler.handle()

        self.server.q.put.assert_called_with({
            "message": "speed",
            "data": {
                "player": 1,
                "value": 13,
            }
        })
        request.sendall.assert_called_with(b"OK")

    def test_speed_c(self):
        request = self.mock_request("p3s9")
       
        handler = s.TCPHandler(request, None, self.server)
        handler.handle()

        self.server.q.put.assert_called_with({
            "message": "speed",
            "data": {
                "player": 3,
                "value": 9,
            }
        })
        request.sendall.assert_called_with(b"OK")

    def test_speed_invalid_player(self):
        request = self.mock_request("p20s9")
       
        handler = s.TCPHandler(request, None, self.server)
        handler.handle()

        self.server.q.put.assert_not_called()
        request.sendall.assert_called_with(b"ERR")

    def test_speed_invalid_speed(self):
        request = self.mock_request("p2s999")
       
        handler = s.TCPHandler(request, None, self.server)
        handler.handle()

        self.server.q.put.assert_not_called()
        request.sendall.assert_called_with(b"ERR")

    def test_speedinc_a(self):
        request = self.mock_request("p2s+")
       
        handler = s.TCPHandler(request, None, self.server)
        handler.handle()

        self.server.q.put.assert_called_with({
            "message": "speedinc",
            "data": {
                "player": 2,
                "value": 1,
            }
        })
        request.sendall.assert_called_with(b"OK")

    def test_speedinc_b(self):
        request = self.mock_request("p1s-")
       
        handler = s.TCPHandler(request, None, self.server)
        handler.handle()

        self.server.q.put.assert_called_with({
            "message": "speedinc",
            "data": {
                "player": 1,
                "value": -1,
            }
        })
        request.sendall.assert_called_with(b"OK")

    def test_speedinc_c(self):
        request = self.mock_request("p1s+")
       
        handler = s.TCPHandler(request, None, self.server)
        handler.handle()

        self.server.q.put.assert_called_with({
            "message": "speedinc",
            "data": {
                "player": 1,
                "value": 1,
            }
        })
        request.sendall.assert_called_with(b"OK")

    def test_speedinc_invalid_player(self):
        request = self.mock_request("p29s+")
       
        handler = s.TCPHandler(request, None, self.server)
        handler.handle()

        self.server.q.put.assert_not_called()
        request.sendall.assert_called_with(b"ERR")

    def test_speedinc_invalid_symbol(self):
        request = self.mock_request("p2s*")
       
        handler = s.TCPHandler(request, None, self.server)
        handler.handle()

        self.server.q.put.assert_not_called()
        request.sendall.assert_called_with(b"ERR")

if __name__ == "__main__":
    unittest.main()
