import asyncio

from bs4 import BeautifulSoup
from urllib.parse import urljoin

from http_client import HttpClient


class ContentExtractor:
    def __init__(self, http_client: HttpClient, html, url, encoding):
        self.http_client = http_client
        self.soup = BeautifulSoup(html, "html.parser")
        self.url = url
        self.encoding = encoding

    @asyncio.coroutine
    def extract(self):
        # if this is not thread page, return
        if not self.soup.select_one(".mainbox.viewthread"):
            return
        # yield from self.jump_to_author_only_page()

        other_pages_urls = self.get_other_pages_urls()

        soups = [self.soup]

        for other_page_url in other_pages_urls:
            soup = yield from self.http_client.get(other_page_url, self.encoding)
            soups.append(soup)

        content = self.url + "\n"
        for soup in soups:
            content += self.extract_one_page(soup) + "\n"

        title = self.soup.select_one("title").get_text()
        title = title[0:title.index(" - ")]
        file_path = "d:/temp/{}.txt".format(title)
        f = open(file_path, mode="w", encoding="UTF-8")
        f.write(content)
        f.close()
        print("Crawled file {}".format(file_path))

    @asyncio.coroutine
    def jump_to_author_only_page(self):
        link = self.soup.select_one(".mainbox.viewthread").select_one(".postinfo > a[href^=viewthread]")
        absolute_url = urljoin(self.url, link["href"])
        self.soup = yield from self.http_client.get(absolute_url)

    def get_other_pages_urls(self):
        pages = self.soup.select_one(".pages")
        if not pages:
            return []
        links = []
        for link in pages.select("a[href^=thread-]"):
            # skip next page and last page link
            if link.get("class", None) is not None:
                continue
            absolute_url = urljoin(self.url, link["href"])
            links.append(absolute_url)
        return links

    @staticmethod
    def extract_one_page(soup):
        content = ""
        for content_container in soup.select(".mainbox.viewthread div[id^=postmessage_] > div[id^=postmessage_]"):
            if content_container.font:
                content_node = content_container.font
            else:
                content_node = content_container
            content += content_node.get_text() + "\n"
        return content
