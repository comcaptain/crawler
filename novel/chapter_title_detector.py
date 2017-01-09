import re
from enum import Enum
from novel.bean import NovelChapter
from novel.number_parser import ChineseNumberParser


class ChapterTitleDetector:
    def __init__(self):
        self.number_characters = set()
        for c in u'0123456789０１２３４５６７８９一二三四五六七八九零十百千万':
            self.number_characters.add(c)
        self.number_to_number_chapter_regex = re.compile(u'^[\s　]*[0-9０１２３４５６７８９]+[-－—]([0-9０１２３４５６７８９]+)[\s　]*$')
        self.space_regex = re.compile("[\s　]")
        self.section_open_close_map = {u"第": {u"卷", u"集"}}
        self.chapter_open_close_map = {
            u"第": {u"章", u"节", u"回", u"话"},
            u"（": {u"）"},
            u"(": {u")"}
        }

    def detect_chapter_title(self, line) -> NovelChapter:
        match = self.number_to_number_chapter_regex.match(line)
        if match:
            return NovelChapter(ChineseNumberParser(match.group(1)).parse_int(), "")

        current_status = DetectStatus.LINE_BEGINNING
        open_character = None
        chapter_number_str = None
        chapter_name = ""
        index = -1
        for c in line:
            index += 1
            if current_status == DetectStatus.LINE_BEGINNING:
                if self.space_regex.match(c):
                    continue
                if not self.chapter_open_close_map.get(c) and not self.section_open_close_map.get(c):
                    return None
                current_status = DetectStatus.OPENED
                open_character = c
            elif current_status == DetectStatus.OPENED:
                if c not in self.number_characters:
                    return None
                chapter_number_str = c
                current_status = DetectStatus.COLLECTING_NUMBER
            elif current_status == DetectStatus.COLLECTING_NUMBER:
                if c in self.number_characters:
                    chapter_number_str += c
                    continue
                # section number closed
                elif self.section_open_close_map.get(open_character) and c in self.section_open_close_map.get(open_character):
                    chapter_number_str = None
                    open_character = None
                    current_status = DetectStatus.SECTION_NUMBER_CLOSED
                # chapter number closed
                elif self.chapter_open_close_map.get(open_character) and c in self.chapter_open_close_map.get(open_character):
                    # There's no chapter name
                    if index == len(line) - 1:
                        current_status = DetectStatus.DETECTED_END
                        break
                    current_status = DetectStatus.CHAPTER_NUMBER_CLOSED
                else:
                    return None
            elif current_status == DetectStatus.SECTION_NUMBER_CLOSED:
                if self.chapter_open_close_map.get(c):
                    chapter_number_str = None
                    current_status = DetectStatus.OPENED
                    open_character = c
                    continue
                if not self.space_regex.match(c):
                    return None
                current_status = DetectStatus.SCANNING_SECTION_NAME
            elif current_status == DetectStatus.SCANNING_SECTION_NAME:
                if self.chapter_open_close_map.get(c):
                    chapter_number_str = None
                    current_status = DetectStatus.OPENED
                    open_character = c
                    continue
            elif current_status == DetectStatus.CHAPTER_NUMBER_CLOSED:
                # there must be one space after chapter close, e.g. `第三章 英雄`: OK, `第三章英雄`: NG
                if not self.space_regex.match(c):
                    return None
                current_status = DetectStatus.CHAPTER_NAME_COLLECTING
            elif current_status == DetectStatus.CHAPTER_NAME_COLLECTING:
                chapter_name += c

        if current_status != DetectStatus.CHAPTER_NAME_COLLECTING and current_status != DetectStatus.DETECTED_END:
            return None
        if len(chapter_name) > 20:
            return None
        return NovelChapter(ChineseNumberParser(chapter_number_str).parse_int(), chapter_name.replace(u"　", " ").strip())


class DetectStatus(Enum):
    LINE_BEGINNING = 1
    OPENED = 2
    COLLECTING_NUMBER = 3
    SECTION_NUMBER_CLOSED = 4
    SCANNING_SECTION_NAME = 5
    CHAPTER_NUMBER_CLOSED = 6
    CHAPTER_NAME_COLLECTING = 7
    DETECTED_END = 8
