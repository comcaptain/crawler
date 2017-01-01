import asyncio
from crawler import Crawler

loop = asyncio.get_event_loop()

crawler = Crawler("http://www.sexinsex.net/bbs/forum-322-1.html", max_redirect=10, max_tasks=10, loop=loop, encoding="GBK")

loop.run_until_complete(crawler.crawl())
