import asyncio
from crawler import Crawler

loop = asyncio.get_event_loop()

crawler = Crawler("http://www.sexinsex.net/bbs/forum-186-1.html", max_redirect=10, max_tasks=10, loop=loop, encoding="GBK", max_requests_in_one_second=2.5)

loop.run_until_complete(crawler.crawl())
