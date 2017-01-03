import asyncio
import aiohttp
from configparser import ConfigParser
from crawler import Crawler
from http_client import HttpClient
from traffic_controller import TrafficController
from bean import CrawlTarget, LoginInformation, CrawlConfig


# According to http://www.crifan.com/character_encoding_charset_simpile_tutorial/
# GB18030 contains GBK contains GB2312
# So, although it seems that SIS uses GBK, but in fact it contains unicode only contained in GB18030 in some pages
target = CrawlTarget(root_urls=["http://www.sexinsex.net/bbs/forum-405-1.html"], encoding="gb18030")

config = ConfigParser()
config.read('auth.ini')
login_info = LoginInformation(
    form_url="http://www.sexinsex.net/bbs/index.php",
    form_selector="#loginform",
    parameters={"username": config["login"]["username"], "password": config["login"]["password"]},
    check_node_selector=".box.message",
    check_text=u'欢迎您回来')

crawl_config = CrawlConfig(max_tasks=10, max_redirects=10, requests_per_second=2.5)

loop = asyncio.get_event_loop()
http_client = crawl_config.generate_http_client(loop)
crawler = Crawler(crawl_config=crawl_config, http_client=http_client, login_info=login_info, target=target)

loop.run_until_complete(crawler.crawl())