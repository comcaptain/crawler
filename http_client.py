import asyncio
import aiohttp
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from traffic_controller import TrafficController


class HttpClient:
    def __init__(self, session:aiohttp.ClientSession, traffic_controller: TrafficController):
        self.session = session
        self.traffic_controller = traffic_controller

    @asyncio.coroutine
    def get(self, url, encoding) -> BeautifulSoup:
        response = yield from self.get_raw_response(url)
        soup = yield from self._parse_response(response, encoding)
        return soup

    @asyncio.coroutine
    def get_raw_response(self, url):
        yield from self.traffic_controller.wait_before_request()
        print("request for page: {}".format(url))
        response = yield from self.session.get(url, allow_redirects=False)
        print("fetched page: {}".format(url))
        return response

    @asyncio.coroutine
    def submit(self, form_url, form_selector, encoding, parameters):
        soup = yield from self.get(form_url, encoding)

        # generate form parameters
        form_parameters = {}
        tags = soup.select(form_selector + " [name]")
        for tag in tags:
            form_parameters[tag["name"]] = tag.get("value", "")
        form_parameters.update(parameters)

        # get submit target url
        form = soup.select_one(form_selector)
        action = form["action"]
        submit_url = urljoin(form_url, action)

        # get submit method
        method = form.get("method", "GET").upper()

        yield from self.traffic_controller.wait_before_request()

        if method == "GET":
            response = yield from self.session.get(submit_url, **form_parameters)
        else:
            response = yield from self.session.post(submit_url, data=form_parameters)

        soup = yield from self._parse_response(response, encoding)
        return soup

    @asyncio.coroutine
    def _parse_response(self, response, encoding):
        try:
            html = yield from response.text(encoding)
            return BeautifulSoup(html, "html.parser")
        finally:
            yield from response.release()

    def close(self):
        self.session.close()
