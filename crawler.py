from asyncio import Queue
from form import FormSubmitter
from bs4 import BeautifulSoup
import aiohttp
import asyncio


class Crawler:
    def __init__(self, root_url, max_redirect, loop, max_tasks, encoding):
        self.maxTasks = max_tasks
        self.max_redirect = max_redirect
        self.encoding = encoding
        self.q = Queue()
        self.q.put_nowait((root_url, self.max_redirect))
        self.seenUrls = set()

        self.session = aiohttp.ClientSession(loop = loop)
        self.formSubmitter = FormSubmitter(self.session)

    @asyncio.coroutine
    def login(self, login_url, form_selector, parameters):
        login_response = yield from self.formSubmitter.submit(
            login_url=login_url, form_selector=form_selector, parameters=parameters, encoding=self.encoding)
        html = yield from login_response.text(self.encoding)
        soup = BeautifulSoup(html, "html.parser")
        message = soup.select_one(".box.message").string
        if message.find(u'欢迎您回来') != -1:
            print("login successfully: " + message)
            return True

        print("login failed, returned message is " + message)
        return False

    @asyncio.coroutine
    def crawl(self):
        login_successful = yield from self.login(
            login_url="http://www.sexinsex.net/bbs/index.php",
            form_selector="#loginform",
            parameters={"username":"aa", "password": "bbbb"})
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
            url, maxRedirect = yield from self.q.get()
            yield from self.fetch(url, maxRedirect)
            self.q.task_done()

    @asyncio.coroutine
    def fetch(self, url, maxRedirect):
        response = yield from self.session.get(url, allow_redirects=False)

        try:
            if response.status == 302:
                if maxRedirect > 0:
                    nextUrl = response.headers['location']
                    if nextUrl in self.seenUrls:
                        return
                    self.seenUrls.add(nextUrl)
                    self.q.put_nowait((nextUrl, maxRedirect - 1))
            else:
                links = yield from self.parseLinks(response)
                for link in links.difference(self.seenUrls):
                    self.q.put_nowait((link, self.max_redirect))
                self.seenUrls.update(links)
        finally:
            yield from response.release()

    @asyncio.coroutine
    def parseLinks(self, response):
        content = yield from response.text("GBK")
        print(content)
        return {}


