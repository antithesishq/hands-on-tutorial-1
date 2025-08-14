from src.client.client import Client


def start_interactive(host="127.0.0.1", port=7000):
    """Start an interactive client session."""
    client = Client(host, port)
    url = f"http://{host}:{port}"
    print(f"Sending to {url}. Type messages (Ctrl+C to quit).")
    try:
        while True:
            msg = input("> ")
            if not msg:
                continue
            result = client.echo(msg)
            print(f"Echo: {result}")
    except (KeyboardInterrupt, EOFError):
        print("\nDisconnected.")
