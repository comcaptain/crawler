import asyncio
import time


class TrafficController:
    def __init__(self, requests_per_second):
        self.minimum_delay = 1.0 / requests_per_second
        self.last_fetch_time = None

    @asyncio.coroutine
    def wait_before_request(self):
        if self.last_fetch_time is None:
            self.last_fetch_time = time.time()
            return

        while True:
            time_passed_since_last_request = time.time() - self.last_fetch_time
            if time_passed_since_last_request < self.minimum_delay:
                wait_time = self.minimum_delay - time_passed_since_last_request
                yield from asyncio.sleep(wait_time)
            else:
                break
        self.last_fetch_time = time.time()
