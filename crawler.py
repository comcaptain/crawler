import traceback
from asyncio import Queue
from configparser import ConfigParser
import asyncio

from content_extractor import ContentExtractor
from http_client import HttpClient
from link_parser import LinkParser


class Crawler:
    def __init__(self, root_url, max_redirect, max_tasks, encoding, http_client: HttpClient):
        self.max_tasks = max_tasks
        self.max_redirect = max_redirect
        self.encoding = encoding
        self.q = Queue()
        self.q.put_nowait((root_url, self.max_redirect))
        self.seen_urls = set()

        self.http_client = http_client

        self.config = ConfigParser()
        self.config.read('auth.ini')

    @asyncio.coroutine
    def login(self):
        login_url="http://www.sexinsex.net/bbs/index.php"
        form_selector="#loginform"
        parameters = {"username": self.config["login"]["username"], "password": self.config["login"]["password"]}
        soup = yield from self.http_client.submit(
            login_url=login_url, form_selector=form_selector, parameters=parameters, encoding=self.encoding)

        message = soup.select_one(".box.message").get_text()
        if message.find(u'欢迎您回来') != -1:
            print("login successfully: " + message)
            return True
        print("login failed, returned message is " + message)
        return False

    @asyncio.coroutine
    def crawl(self):
        login_successful = yield from self.login()
        if not login_successful:
            return False
        workers = [asyncio.Task(self.work()) for _ in range(self.max_tasks)]
        yield from self.q.join()
        for w in workers:
            w.cancel()
        self.http_client.close()

    @asyncio.coroutine
    def work(self):
        while True:
            url, max_redirect = yield from self.q.get()
            yield from self.fetch(url, max_redirect)
            self.q.task_done()

    @asyncio.coroutine
    def fetch(self, url, max_redirect):
        response = yield from self.http_client.get_raw_response(url)
        try:
            if response.status == 302:
                if max_redirect > 0:
                    next_url = response.headers['location']
                    if next_url in self.seen_urls:
                        return
                    self.seen_urls.add(next_url)
                    self.q.put_nowait((next_url, max_redirect - 1))
            else:
                html = yield from response.text(self.encoding)
                links = LinkParser(html, url).parse_links()
                if not links:
                    yield from ContentExtractor(http_client=self.http_client, html=html, url=url, encoding=self.encoding).extract()
                for link in links.difference(self.seen_urls):
                    self.q.put_nowait((link, self.max_redirect))
                self.seen_urls.update(links)
        except Exception as exp:
            print("Error happendsing while crawing page {}: {}".format(url, exp))
            traceback.print_exc()
        finally:
            response.release()
