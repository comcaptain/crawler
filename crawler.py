from asyncio import Queue
from configparser import ConfigParser
from form import FormSubmitter
from bs4 import BeautifulSoup
import aiohttp
import asyncio
from link_parser import LinkParser
import time
from traffic_controller import TrafficController


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

        self.traffic_controller = TrafficController(max_requests_in_one_second)

    @asyncio.coroutine
    def login(self):
        login_url="http://www.sexinsex.net/bbs/index.php"
        form_selector="#loginform"
        parameters = {"username": self.config["login"]["username"], "password": self.config["login"]["password"]}

        login_response = yield from self.formSubmitter.submit(
            login_url=login_url, form_selector=form_selector, parameters=parameters, encoding=self.encoding)
        try:
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
        yield from self.traffic_controller.wait_before_request()

        print("request for page(max_redirect={}): {}".format(max_redirect, url))
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
