from asyncio import Queue
import aiohttp
import asyncio

class Crawler:
    def __init__(self, rootUrl, maxRedirect, loop, maxTasks):
        self.maxTasks = maxTasks
        self.maxRedirect = maxRedirect
        self.q = Queue()
        self.q.put_nowait((rootUrl, self.maxRedirect))
        self.seenUrls = set()

        self.session = aiohttp.ClientSession(loop = loop)

    @asyncio.coroutine
    def crawl(self):
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
                    self.q.put_nowait((link, self.maxRedirect))
                self.seenUrls.update(links)
        finally:
            yield from response.release()

    @asyncio.coroutine
    def parseLinks(self, response):
        content = yield from response.text("GBK")
        print(content)
        return {}


