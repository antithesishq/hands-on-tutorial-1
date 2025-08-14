import argparse

from src.monitor.monitor import start_monitor

parser = argparse.ArgumentParser(description="Echo server monitor")
parser.add_argument("--host", default="127.0.0.1", help="server hostname (default: 127.0.0.1)")
parser.add_argument("--port", type=int, default=7000, help="server port (default: 7000)")
parser.add_argument("--stats-interval", type=int, default=3, help="seconds between prints (default: 3)")
parser.add_argument("--health-interval", type=int, default=1, help="seconds between health checks (default: 1)")
parser.add_argument("--alert-interval", type=int, default=10, help="warn if unhealthy or requests served for this many seconds (default: 10)")
args = parser.parse_args()

try:
    start_monitor(host=args.host, port=args.port, stats_interval=args.stats_interval,
                  health_interval=args.health_interval, alert_interval=args.alert_interval)
except KeyboardInterrupt:
    print("Shutting down")
