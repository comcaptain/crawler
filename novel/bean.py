from typing import List


class NovelChapter:
    def __init__(self, chapter_number: int, chapter_name: str, section_number: int = None, content: str = ''):
        self.chapter_number = chapter_number
        self.chapter_name = chapter_name
        self.section_number = section_number
        self.content = content

    def get_chapter_name(self):
        return u"{}第{}章 {}".format(
            u'第{}卷 '.format(self.section_number) if self.section_number else "",
            self.chapter_number,
            self.chapter_name)

class Novel:
    def __init__(self, name: str, foreword: str, chapters: List[NovelChapter]):
        self.name = name
        self.foreword = foreword
        self.chapters = chapters