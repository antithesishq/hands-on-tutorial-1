import threading
import time
from pathlib import Path

from antithesis.assertions import unreachable
from antithesis.lifecycle import setup_complete
from antithesis.random import AntithesisRandom
from src.client.client import Client

def wait_for_server_up(host="127.0.0.1", port=7000):
    client = Client(host, port)
    print(f"Waiting for server http://{host}:{port}")
    while True:
        time.sleep(1)
        try:
            client.health()
            print("Server is up, issuing setup complete")
            setup_complete(details={})
            return
        except Exception as e:
            print(f"Health-check failed: {e}")

def start_workload(host="127.0.0.1", port=7000, verbose=False, alert_interval=10):
    """
    Run workload against the echo server.
    Check for valid responses and for (eventual) progress.
    """

    # Load dictionary file used to create requests
    words_path = Path(__file__).parent / "words.txt"
    words = words_path.read_text().splitlines()

    # Initialize some statistics
    success_count = 0
    error_count = 0
    invalid_response_count = 0
    last_successful_request = time.monotonic()
    # How often to print statistics
    stats_interval = 5

    def print_stats_task():
        """
        Print statistics at regular intervals
        """
        while True:
            time.sleep(stats_interval)
            print(f"Success: {success_count} Errors: {error_count} Invalid response: {invalid_response_count}")

    # Fork statistics task (not thread-safe, but that's alright...)
    threading.Thread(target=print_stats_task, daemon=True).start()

    # Create a client
    client = Client(host, port)
    # Initialize RNG
    rng = AntithesisRandom()

    print(f"Starting workload against http://{host}:{port}")
    while True:
        # Has it been too long since the last successful request?
        since_last_success = time.monotonic() - last_successful_request
        if since_last_success > alert_interval:
            print(f"WARNING: {since_last_success:.1f}s since the last successful request")
            # Flag this as something that should never happen
            details = {
                "last_successful_request": since_last_success,
                "alert_threshold": alert_interval,
            }
            unreachable("Server unavailable for too long (workload requests)", details)

        # Create the next request body:
        count = rng.randint(3, 15)
        message = " ".join(rng.choices(words, k=count))

        # Issue the next request:
        try:
            response = client.echo(message)
        except KeyboardInterrupt:
            raise
        except Exception as e:
            error_count += 1
            print(f"Request failed: {e}")
            # Back off a little, server may be down
            time.sleep(1)
            continue

        # Request was successful
        last_successful_request = time.monotonic()

        # Check response
        if response == message:
            success_count += 1
            if verbose:
                print(f"OK: {message}")
        else:
            print(f"Invalid response! Sent '{message!r}', Received '{response!r}'")
            invalid_response_count += 1
            # Flag this as something that should never-ever happen. If it does, surface it in the report
            details = {
                "sent": message,
                "received": response,
            }
            unreachable("Invalid echo response", details)
