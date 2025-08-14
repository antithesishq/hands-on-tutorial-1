import argparse

from src.client.interactive import start_interactive

parser = argparse.ArgumentParser(description="HTTP echo client")
parser.add_argument("--host", default="127.0.0.1", help="server hostname (default: 127.0.0.1)")
parser.add_argument("--port", type=int, default=7000, help="server port (default: 7000)")
args = parser.parse_args()

start_interactive(host=args.host, port=args.port)
