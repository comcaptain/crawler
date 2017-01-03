from typing import List, Dict

import aiohttp

from http_client import HttpClient
from traffic_controller import TrafficController


class CrawlTarget:
    def __init__(self, root_urls: List[str], encoding: str):
        self.root_urls = root_urls
        self.encoding = encoding


class LoginInformation:
    """
    Information used to login to crawling target website
    @param form_url: url of page that has login form
    @param form_selector: css selector of login form
    @param parameters: parameters that we want to override for login form, e.g. username and password
    @param check_node_selector: css selector of node in post result page, this node is used to check for login success
    @param check_text: if login is successful, then result page's `check_node`'s text should contain this
    """
    def __init__(self,
                 form_url: str,
                 form_selector: str,
                 parameters: Dict[str, str],
                 check_node_selector: str,
                 check_text: str):
        self.form_url = form_url
        self.form_selector = form_selector
        self.parameters = parameters
        self.check_node_selector = check_node_selector
        self.check_text = check_text


class CrawlConfig:
    def __init__(self, max_tasks: int, max_redirects: int, requests_per_second: float):
        self.max_task = max_tasks
        self.max_redirects = max_redirects
        self.requests_per_second = requests_per_second

    def generate_http_client(self, loop):
        return HttpClient(aiohttp.ClientSession(loop=loop), TrafficController(self.requests_per_second))
