import argparse

from src.server.server import start

parser = argparse.ArgumentParser(description="HTTP echo server")
parser.add_argument("--host", default="127.0.0.1", help="hostname to bind to (default: 127.0.0.1)")
parser.add_argument("--port", type=int, default=7000, help="port to listen on (default: 7000)")
parser.add_argument("--verbose", action="store_true", help="enable request logging")
args = parser.parse_args()


try:
    start(host=args.host, port=args.port, verbose=args.verbose)
except KeyboardInterrupt:
    print("\nShutting down.")
