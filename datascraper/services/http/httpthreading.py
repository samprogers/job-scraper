from concurrent.futures import ThreadPoolExecutor
import time, requests

class HttpThreading():

    max_workers = 5
    sleep_every = 10
    sleep_time = 15

    thread_counter = 1
    current_callback = None
    last_responses = {}

    def __init__(self, max_workers=5, sleep_every=10, sleep_time=15):
        self.max_workers = max_workers
        self.sleep_every = sleep_every
        self.sleep_time = sleep_time

    def wrapRequest(self, url: str) -> str | None:
        self.thread_counter += 1
        if self.thread_counter % self.sleep_every == 0:
            time.sleep(self.sleep_time)

        try:
            rsp = requests.get(url)
            print(len(rsp.text))
            print(self.thread_counter)

            if callable(self.current_callback):
                self.current_callback(url)


            self.last_responses[url] = rsp.text
            if rsp.status_code <= 299:
                print(rsp.status_code)
                return rsp.text
            elif rsp.status_code == 429:
                time.sleep(self.sleep_every)
                rsp = requests.get(url)
                print(rsp.status_code)
                return rsp.text if rsp.status_code == 200 else None
            else:
                return None

        except Exception as e:
            print("ERROR: " + str(e))
            return None


    def executeGet(self, urls: list, callback=None) -> list:

        with ThreadPoolExecutor(max_workers=10) as executor:
            self.current_callback = callback
            return list(executor.map(self.wrapRequest, urls))

    def getLastResponse(self, url) -> str:
        return self.last_responses[url] if url in self.last_responses.keys() else ""

