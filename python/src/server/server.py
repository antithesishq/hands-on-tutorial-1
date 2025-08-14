import datetime
import json
from http.server import BaseHTTPRequestHandler, HTTPServer

from src.server.stats import Stats


class EchoHandler(BaseHTTPRequestHandler):
    stats = Stats()
    RECENT_REQUESTS = []
    MAX_RECENT_REQUESTS = 15

    GET_ROUTES = {
        "/health": lambda self: self.handle_health(),
        "/stats": lambda self: self.handle_stats(),
    }
    POST_ROUTES = {
        "/echo": lambda self: self.handle_echo(),
    }

    def do_GET(self):
        handler = self.GET_ROUTES.get(self.path)
        if handler:
            handler(self)
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        handler = self.POST_ROUTES.get(self.path)
        if handler:
            handler(self)
        else:
            self.send_response(404)
            self.end_headers()

    def handle_echo(self):
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length)
        self.stats.record_request(self.client_address, length)
        EchoHandler.save_request(body)
        response_body = self.process_echo_request(body)

        self.send_response(200)
        self.send_header(
            "Content-Type", self.headers.get("Content-Type", "application/octet-stream")
        )
        self.send_header("Content-Length", str(len(response_body)))
        self.end_headers()

        self.wfile.write(response_body)
        self.stats.record_response()

    def handle_health(self):
        body = b"OK"
        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def handle_stats(self):
        now = datetime.datetime.now(datetime.timezone.utc)
        uptime = (now - self.stats.created_at).total_seconds()
        data = {
            "request_count": self.stats.request_count,
            "response_count": self.stats.response_count,
            "total_data": self.stats.total_data,
            "uptime_seconds": uptime,
        }
        body = json.dumps(data).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def process_echo_request(self, request_body):
        # Artificial "One in a million" bug. {*}
        with open("/dev/urandom", "rb") as f:
            r = int.from_bytes(f.read(4), "big")
            if r % 1_000_000 == 0:
                return "Surprise!".encode("utf-8")
        # Correct response:
        return request_body

    def log_message(self, format, *args):
        if self.server.verbose:
            super().log_message(format, *args)

    @classmethod
    def save_request(cls, request_body):
        # Save the last request, useful for debugging in case of crash
        EchoHandler.RECENT_REQUESTS.append(request_body)
        # Only retain the most recent MAX_RECENT_REQUESTS requests
        if len(EchoHandler.RECENT_REQUESTS) > EchoHandler.MAX_RECENT_REQUESTS:
            EchoHandler.RECENT_REQUESTS[-EchoHandler.MAX_RECENT_REQUESTS:] # {*}

    @classmethod
    def print_last_request(cls, n):
        last_n_requests = EchoHandler.RECENT_REQUESTS[-n:]
        if len(last_n_requests) == 0:
            print("No requests received")
        else:
            print(f"Last {len(last_n_requests)} requests: ")
            for r in last_n_requests:
                print(f" - {r!r}")


def start(host="127.0.0.1", port=7000, verbose=False):
    # Create server
    server = HTTPServer((host, port), EchoHandler)
    server.verbose = verbose

    # Listen and serve requests
    print(f"Echo server listening on http://{host}:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        raise
    except Exception as e:
        print(f"Fatal error: {e}")
        EchoHandler.print_last_request(3)
    finally:
        server.server_close()
