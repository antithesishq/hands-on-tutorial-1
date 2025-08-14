import json
import threading
import unittest
from http.server import HTTPServer
from urllib.request import Request, urlopen

from src.server.server import EchoHandler


def _start_server():
    """Start an EchoHandler server on an OS-assigned port and return (server, url)."""
    server = HTTPServer(("127.0.0.1", 0), EchoHandler)
    server.verbose = False
    host, port = server.server_address
    url = f"http://{host}:{port}"
    thread = threading.Thread(target=server.serve_forever)
    thread.daemon = True
    thread.start()
    return server, url


def _post(url, body, content_type="text/plain"):
    req = Request(url, data=body.encode(), method="POST")
    req.add_header("Content-Type", content_type)
    with urlopen(req) as resp:
        return resp.status, resp.headers, resp.read()


def _get(url):
    req = Request(url, method="GET")
    with urlopen(req) as resp:
        return resp.status, resp.headers, resp.read()


class TestEchoHandler(unittest.TestCase):
    def setUp(self):
        self.server, self.url = _start_server()
        self.echo_url = self.url + "/echo"

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()

    def test_post_echoes_body(self):
        status, _, body = _post(self.echo_url, "hello")
        self.assertEqual(status, 200)
        self.assertEqual(body, b"hello")

    def test_post_preserves_content_type(self):
        _, headers, _ = _post(self.echo_url, '{"a":1}', "application/json")
        self.assertEqual(headers["Content-Type"], "application/json")

    def test_post_returns_correct_content_length(self):
        msg = "test message"
        _, headers, _ = _post(self.echo_url, msg)
        self.assertEqual(headers["Content-Length"], str(len(msg)))

    def test_post_empty_body(self):
        status, headers, body = _post(self.echo_url, "")
        self.assertEqual(status, 200)
        self.assertEqual(body, b"")
        self.assertEqual(headers["Content-Length"], "0")

    def test_post_unicode(self):
        msg = "caf\u00e9 \u2603"
        status, _, body = _post(self.echo_url, msg)
        self.assertEqual(status, 200)
        self.assertEqual(body, msg.encode("utf-8"))

class TestHealthHandler(unittest.TestCase):
    def setUp(self):
        self.server, self.url = _start_server()

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()

    def test_health_returns_200_ok(self):
        status, _, body = _get(self.url + "/health")
        self.assertEqual(status, 200)
        self.assertEqual(body, b"OK")


class TestStatsHandler(unittest.TestCase):
    def setUp(self):
        self.server, self.url = _start_server()

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()

    def test_stats_returns_json(self):
        status, headers, body = _get(self.url + "/stats")
        self.assertEqual(status, 200)
        self.assertEqual(headers["Content-Type"], "application/json")
        data = json.loads(body)
        for key in ("request_count", "response_count", "total_data", "uptime_seconds"):
            self.assertIn(key, data)

    def test_stats_counts_requests(self):
        _, _, body = _get(self.url + "/stats")
        before = json.loads(body)
        for _ in range(3):
            _post(self.url + "/echo", "hello")
        _, _, body = _get(self.url + "/stats")
        after = json.loads(body)
        self.assertEqual(after["request_count"] - before["request_count"], 3)
        self.assertEqual(after["response_count"] - before["response_count"], 3)


if __name__ == "__main__":
    unittest.main()
