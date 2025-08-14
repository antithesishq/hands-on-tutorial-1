import datetime


class Stats:
    def __init__(self):
        self.created_at = datetime.datetime.now(datetime.timezone.utc)
        self.request_count = 0
        self.response_count = 0
        self.total_data = 0
        self.requests_by_client = {}

    def record_request(self, client_address, request_length):
        self.request_count += 1
        self.requests_by_client[client_address] = 1 + self.requests_by_client.get(client_address, 0)
        self.total_data += request_length

    def record_response(self):
        self.response_count += 1
