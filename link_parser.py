from bs4 import BeautifulSoup
from urllib.parse import urljoin


class LinkParser:
    def __init__(self, html, url):
        self.url = url
        self.soup = BeautifulSoup(html, "html.parser")

    def parse_links(self):
        tables = self.soup.select("table[id^=forum_]")
        if tables:
            return self.parse_forum_detail(tables)
        return set()

    def parse_forum_detail(self, tables):
        links = set()

        # get thread links #
        tables_count = len(tables)
        # if it's first page, then there'll be more than 2 tables, for other pages, it can have two tables:
        # 推荐主题 and 版块主题
        if tables_count <= 2:
            target_tables = tables
        else:
            target_tables = [tables[tables_count - 1]]
        for table in target_tables:
            for link in table.select("span[id^=thread_] > a[href]"):
                absolute_url = urljoin(self.url, link["href"])
                links.add(absolute_url)
                print("got thread link: {}:{}".format(link.get_text(), absolute_url))

        # get other pages' link
        pages = self.soup.select_one(".pages")
        for link in pages.select("a[href^=forum-]"):
            # skip next page and last page link
            if link.get("class", None) is not None:
                continue
            absolute_url = urljoin(self.url, link["href"])
            links.add(absolute_url)
            print("got other page's link: {}:{}".format(link.get_text(), absolute_url))

        return links
