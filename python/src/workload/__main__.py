import argparse

from src.workload.workload import start_workload, wait_for_server_up

parser = argparse.ArgumentParser(description="HTTP echo workload")
parser.add_argument("--host", default="127.0.0.1", help="server hostname (default: 127.0.0.1)")
parser.add_argument("--port", type=int, default=7000, help="server port (default: 7000)")
parser.add_argument("--verbose", action="store_true", help="enable request logging")
parser.add_argument("--alert-interval", type=int, default=10, help="warn if unable to complete a request for this many seconds (default: 10)")
args = parser.parse_args()

try:
    wait_for_server_up(host=args.host, port=args.port)
    start_workload(host=args.host, port=args.port, verbose=args.verbose, alert_interval=args.alert_interval)
except KeyboardInterrupt:
    print("Shutting down")
