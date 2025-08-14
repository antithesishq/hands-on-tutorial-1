import threading
import unittest
from http.server import HTTPServer

from src.client.client import Client
from src.server.server import EchoHandler


def _start_server():
    server = HTTPServer(("127.0.0.1", 0), EchoHandler)
    server.verbose = False
    thread = threading.Thread(target=server.serve_forever)
    thread.daemon = True
    thread.start()
    return server


class TestEcho(unittest.TestCase):
    def setUp(self):
        self.server = _start_server()
        host, port = self.server.server_address
        self.client = Client(host, port)

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()

    def test_echo_returns_echoed_message(self):
        result = self.client.echo("hello")
        self.assertEqual(result, "hello")

    def test_echo_empty_string(self):
        result = self.client.echo("")
        self.assertEqual(result, "")

    def test_echo_unicode(self):
        msg = "caf\u00e9 \u2603"
        result = self.client.echo(msg)
        self.assertEqual(result, msg)

    def test_echo_long_message(self):
        msg = "a" * 10_000
        result = self.client.echo(msg)
        self.assertEqual(result, msg)


if __name__ == "__main__":
    unittest.main()
