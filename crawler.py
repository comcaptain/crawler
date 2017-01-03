import asyncio
import traceback
from asyncio import Queue
from sis.link_parser import LinkParser
from bean import CrawlTarget, CrawlConfig, LoginInformation
from http_client import HttpClient
from sis.content_extractor import ContentExtractor


class Crawler:
    def __init__(self, target: CrawlTarget, crawl_config: CrawlConfig, http_client: HttpClient, login_info: LoginInformation = None):
        self.max_tasks = crawl_config.max_task
        self.max_redirect = crawl_config.max_redirects
        self.encoding = target.encoding
        self.http_client = http_client
        self.login_information = login_info

        self.q = Queue()
        for url in target.root_urls:
            self.q.put_nowait((url, self.max_redirect))

        self.seen_urls = set()

    @asyncio.coroutine
    def login(self) -> bool:
        # do not do login if login_information is absent
        if not self.login_information:
            return True

        soup = yield from self.http_client.submit(
            form_url=self.login_information.form_url,
            form_selector=self.login_information.form_selector,
            parameters=self.login_information.parameters,
            encoding=self.encoding)

        message = soup.select_one(self.login_information.check_node_selector).get_text()
        if message.find(self.login_information.check_text) != -1:
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
