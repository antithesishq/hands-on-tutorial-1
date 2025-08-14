import requests

DEFAULT_TIMEOUT=(20, 20) # Connect and read timeouts # {*}

class Client:
    def __init__(self, host="127.0.0.1", port=7000):
        self.host = host
        self.port = port

    def echo(self, message, timeout=DEFAULT_TIMEOUT):
        """Send a message to the echo server via HTTP POST and return the response."""
        url = f"http://{self.host}:{self.port}/echo"
        encoded_message = message.encode()
        with requests.post(url, data=encoded_message,
                                headers={
                                    "Content-Type": "application/octet-stream",
                                    "Content-Length": str(len(encoded_message)),
                                },
                                timeout=timeout) as resp:
            resp.raise_for_status()
            return resp.content.decode()

    def stats(self, timeout=DEFAULT_TIMEOUT):
        """Fetch server statistics and return them as a dictionary."""
        with requests.get(f"http://{self.host}:{self.port}/stats", timeout=timeout) as resp:
            resp.raise_for_status()
            return resp.json()

    def health(self, timeout=DEFAULT_TIMEOUT):
        """Fetch server health and return the response body as a string."""
        with requests.get(f"http://{self.host}:{self.port}/health", timeout=timeout) as resp:
            resp.raise_for_status()
            return resp.text
