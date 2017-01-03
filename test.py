import asyncio

import aiohttp

from crawler import Crawler
from http_client import HttpClient
from traffic_controller import TrafficController

loop = asyncio.get_event_loop()

http_client = HttpClient(aiohttp.ClientSession(loop = loop), TrafficController(2.5))

crawler = Crawler("http://www.sexinsex.net/bbs/forum-405-1.html", max_redirect=10, max_tasks=10, http_client=http_client, encoding="GBK")

loop.run_until_complete(crawler.crawl())