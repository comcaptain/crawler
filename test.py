import asyncio
from crawler import Crawler

loop = asyncio.get_event_loop()

crawler = Crawler("http://www.sexinsex.net/bbs/index.php", 10, loop, 10)

loop.run_until_complete(crawler.crawl())
