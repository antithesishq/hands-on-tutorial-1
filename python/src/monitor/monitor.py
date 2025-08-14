import time

from src.client.client import Client

from antithesis.assertions import unreachable


class Monitor:
    def __init__(self, host="127.0.0.1", port=7000, stats_interval=1,
                 health_interval=1, alert_interval=10):
        self.client = Client(host, port)
        self.host_port = f"{host}:{port}"
        self.stats_interval = stats_interval
        self.health_interval = health_interval
        self.alert_interval = alert_interval

        self.empty_stats = {
            "request_count": 0,
            "response_count": 0,
            "total_data": 0,
            "uptime_seconds": 0,
        }
        self.previous_stats = self.empty_stats
        self.current_stats = self.empty_stats

        now = time.monotonic()
        self._last_stats_print = now
        self._last_health_check = now
        self._last_healthy = now

    def run(self):
        while True:
            time.sleep(0.5)
            now = time.monotonic()
            # Time for the next health-check?
            if now > self._last_health_check + self.health_interval:
                self._last_health_check = now
                self._check_health(now)
            # Time for the next stats update?
            if now > self._last_stats_print + self.stats_interval:
                self._last_stats_print = now
                self._fetch_and_print_stats(now)

    def _check_health(self, now):
        try:
            status = self.client.health()
            self._last_healthy = now
        except KeyboardInterrupt:
            raise
        except Exception as e:
            # Log error and continue below
            print(f"Health-check failed: {e}")

        # Is it been too long since the last successful healtcheck?
        since_last_healthy = now - self._last_healthy
        if since_last_healthy > self.alert_interval:
            print(f"WARNING: {since_last_healthy:.1f}s since last successful health-check")
            # Flag this state as something that should never happen to surface it in the report
            details = {
                "last_healthcheck": since_last_healthy,
                "alert_threshold": self.alert_interval,
            }
            unreachable("Server unavailable for too long (monitor health-check)", details)

    def _fetch_and_print_stats(self, now):
        try:
            s = self.client.stats()
        except KeyboardInterrupt:
            raise
        except Exception as e:
            print(f"Failed to fetch stats: {e}")
            return

        self.previous_stats = self.current_stats
        self.current_stats = s

        # Simple check to detect a server crash: uptime decreased
        if self.current_stats['uptime_seconds'] < self.previous_stats['uptime_seconds']:
            print(f"WARNING: server uptime decreased: likely a crash-restart")
            # Flag this state as something that should never happen to surface it in the report
            details = {
                "previous_uptime": self.previous_stats['uptime_seconds'],
                "current_uptime": self.current_stats['uptime_seconds'],
            }
            unreachable("Unexpected server restart", details)
            # Reset previous_stats to avoid negative deltas
            self.previous_stats = self.empty_stats

        def delta(key):
            return self.current_stats[key] - self.previous_stats[key]

        def human_readable_size(size):
            units = ["B", "KiB", "MiB", "GiB"]
            for unit in units[:-1]:
                if abs(size) < 1024:
                    return f"{size:.1f}{unit}"
                size /= 1024
            return f"{size:.1f}{units[-1]}"

        now = time.monotonic()
        print(
            f"{self.host_port}: "
            f"last_healthy={(now - self._last_healthy):.1f}s "
            f"up={s['uptime_seconds']:.1f}s "
            f"requests={s['request_count']} (+{delta('request_count')}) "
            f"responses={s['response_count']} (+{delta('response_count')}) "
            f"total_data={human_readable_size(s['total_data'])} (+{human_readable_size(delta('total_data'))})"
        )

def start_monitor(host="127.0.0.1", port=7000, stats_interval=3,
                  health_interval=1, alert_interval=10):
    Monitor(host, port, stats_interval, health_interval, alert_interval).run()
