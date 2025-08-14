import os
import random
import string
import threading
import unittest
from http.server import HTTPServer

from src.client.client import Client
from src.server.server import EchoHandler

NUM_REQUESTS = 100
RANDOM_SEED = 42
MIN_REQUEST_SIZE = 0
MAX_REQUEST_SIZE = 1024*1024*10 # 10MiB


_CHARS = string.ascii_letters + string.digits + string.punctuation + " "
_TABLE = bytes.maketrans(
    bytes(range(256)),
    bytes(ord(_CHARS[b % len(_CHARS)]) for b in range(256)),
)


def _random_string(length):
    return os.urandom(length).translate(_TABLE).decode("ascii")


class TestEndToEnd(unittest.TestCase):
    def setUp(self):
        self.server = HTTPServer(("127.0.0.1", 0), EchoHandler)
        self.server.verbose = False
        thread = threading.Thread(target=self.server.serve_forever)
        thread.daemon = True
        thread.start()
        host, port = self.server.server_address
        self.client = Client(host, port)

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()

    def test_random_requests(self):
        rng = random.Random(RANDOM_SEED)
        for i in range(NUM_REQUESTS):
            length = rng.randint(MIN_REQUEST_SIZE, MAX_REQUEST_SIZE)
            msg = _random_string(length)
            result = self.client.echo(msg)
            self.assertEqual(result, msg, f"mismatch on request {i}")


if __name__ == "__main__":
    unittest.main()
