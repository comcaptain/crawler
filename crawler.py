from asyncio import Queue
from configparser import ConfigParser
from form import FormSubmitter
from bs4 import BeautifulSoup
import aiohttp
import asyncio
from link_parser import LinkParser
import time


class Crawler:
    def __init__(self, root_url, max_redirect, loop, max_tasks, encoding, max_requests_in_one_second=2):
        self.maxTasks = max_tasks
        self.max_redirect = max_redirect
        self.encoding = encoding
        self.q = Queue()
        self.q.put_nowait((root_url, self.max_redirect))
        self.seen_urls = set()

        self.session = aiohttp.ClientSession(loop = loop)
        self.formSubmitter = FormSubmitter(self.session)

        self.config = ConfigParser()
        self.config.read('auth.ini')

        self.minimum_delay = 1.0 / max_requests_in_one_second
        self.last_fetch_time = None

        self.request_sent = 0

    @asyncio.coroutine
    def login(self):
        login_url="http://www.sexinsex.net/bbs/index.php"
        form_selector="#loginform"
        parameters = {"username": self.config["login"]["username"], "password": self.config["login"]["password"]}

        try:
            login_response = yield from self.formSubmitter.submit(
                login_url=login_url, form_selector=form_selector, parameters=parameters, encoding=self.encoding)
            html = yield from login_response.text(self.encoding)
            soup = BeautifulSoup(html, "html.parser")
            message = soup.select_one(".box.message").get_text()
            if message.find(u'欢迎您回来') != -1:
                print("login successfully: " + message)
                return True

            print("login failed, returned message is " + message)
            return False
        finally:
            yield from login_response.release()

    @asyncio.coroutine
    def delay_http_request(self):
        if self.last_fetch_time is None:
            self.last_fetch_time = time.time()
            return

        while True:
            time_passed_since_last_request = time.time() - self.last_fetch_time
            if time_passed_since_last_request < self.minimum_delay:
                wait_time = self.minimum_delay - time_passed_since_last_request
                # print("Wait {:.2f} seconds to send next http request".format(wait_time))
                yield from asyncio.sleep(wait_time)
                # print("Waited {:.2f} seconds".format(wait_time))
            else:
                break

        self.last_fetch_time = time.time()

    @asyncio.coroutine
    def crawl(self):
        login_successful = yield from self.login()
        if not login_successful:
            return False
        workers = [asyncio.Task(self.work()) for _ in range(self.maxTasks)]
        yield from self.q.join()
        for w in workers:
            w.cancel()
        self.session.close()

    @asyncio.coroutine
    def work(self):
        while True:
            url, max_redirect = yield from self.q.get()
            yield from self.fetch(url, max_redirect)
            self.q.task_done()

    @asyncio.coroutine
    def fetch(self, url, max_redirect):
        yield from self.delay_http_request()

        self.request_sent += 1
        print("{} request for page(max_redirect={}): {}".format(self.request_sent, max_redirect, url))
        response = yield from self.session.get(url, allow_redirects=False)

        try:
            if response.status == 302:
                if max_redirect > 0:
                    nextUrl = response.headers['location']
                    if nextUrl in self.seen_urls:
                        return
                    self.seen_urls.add(nextUrl)
                    self.q.put_nowait((nextUrl, max_redirect - 1))
            else:
                html = yield from response.text(self.encoding)
                print("fetched page(max_redirect={}): {}".format(max_redirect, url))
                links = LinkParser(html, url).parse_links()
                for link in links.difference(self.seen_urls):
                    self.q.put_nowait((link, self.max_redirect))
                self.seen_urls.update(links)
        finally:
            yield from response.release()
