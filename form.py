import asyncio
from urllib.parse import urljoin
from bs4 import BeautifulSoup


class FormSubmitter:
    def __init__(self, session):
        self.session = session

    @asyncio.coroutine
    def submit(self, login_url, form_selector, encoding, parameters):
        response = yield from self.session.get(login_url)
        html = yield from response.text(encoding)
        soup = BeautifulSoup(html, "html.parser")
        tags = soup.select(form_selector + " [name]")
        form_parameters = {}
        for tag in tags:
            form_parameters[tag["name"]] = tag.get("value", "")
        form_parameters.update(parameters)

        for key, value in form_parameters.items():
            print("{}={}".format(key, value))

        form = soup.select_one(form_selector)
        action = form["action"]
        submit_url = urljoin(login_url, action)
        method = form.get("method", "GET").upper()

        if method == "GET":
            response = yield from self.session.get(submit_url, **form_parameters)
        else:
            response = yield from self.session.post(submit_url, data=form_parameters)
        return response
