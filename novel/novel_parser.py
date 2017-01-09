from os import listdir
from os.path import isfile, join
import os

import time

from novel.bean import NovelChapter, Novel
from novel.chapter_title_detector import ChapterTitleDetector


class NovelParser:
    def __init__(self):
        self.state = ForewordState()
        self.chapter_title_detector = ChapterTitleDetector()

    def parse_line(self, line):
        chapter = self.chapter_title_detector.detect_chapter_title(line)
        if chapter:
            self.state = self.state.consume_chapter_title_line(chapter.chapter_name, chapter.chapter_number, line)
        else:
            self.state.consume_normal_line(line)

    def end(self, novel_name: str) -> Novel:
        return self.state.end(novel_name)


class ParseState:
    def consume_chapter_title_line(self, chapter_name: str, chapter_number: int, line: str):
        pass

    def consume_normal_line(self, line: str):
        pass

    def end(self, novel_name: str) -> Novel:
        pass


class ForewordState(ParseState):
    def __init__(self):
        self.foreword = ''
        self.last_chapter_title_line = None
        self.last_chapter_name = None
        self.last_chapter_number = None
        self.accumulated_text = []

    def consume_chapter_title_line(self, chapter_name: str, chapter_number: int, line: str) -> ParseState:
        if not self.last_chapter_title_line or chapter_number != 2 or len(self.accumulated_text) < 5:
            if self.last_chapter_title_line:
                self.foreword += self.last_chapter_title_line + '\n'
            self.foreword += "\n".join(self.accumulated_text) + '\n'
            self.accumulated_text = []
            self.last_chapter_name = chapter_name
            self.last_chapter_number = chapter_number
            self.last_chapter_title_line = line
            return self
        return ContentState(
            NovelChapter(self.last_chapter_number, self.last_chapter_name, content="\n".join(self.accumulated_text)),
            NovelChapter(chapter_number, chapter_name),
            self.foreword)

    def consume_normal_line(self, line: str):
        self.accumulated_text.append(line)

    def end(self, novel_name: str) -> Novel:
        return Novel(novel_name, "", [NovelChapter(1, "", content=self.foreword + '\n' + "\n".join(self.accumulated_text))])


class ContentState(ParseState):
    def __init__(self, first_chapter: NovelChapter, second_chapter: NovelChapter, foreword: str):
        self.chapters = [first_chapter]
        self.foreword = foreword
        self.accumulated_text = []
        self.current_chapter = second_chapter
        self.current_section_number = None
        self.warnings = []

    def warn(self, warning):
        print(warning)
        self.warnings.append(warning)

    def consume_chapter_title_line(self, chapter_name: str, chapter_number: int, line: str) -> ParseState:
        last_chapter = self.current_chapter
        self.current_chapter = NovelChapter(chapter_number, chapter_name)
        # duplicate chapter title
        if len(self.accumulated_text) < 5 and chapter_number == last_chapter.chapter_number:
            self.accumulated_text = []
            return self

        if chapter_number == 1:
            if self.current_section_number:
                self.current_section_number += 1
            else:
                for chapter in self.chapters:
                    chapter.section_number = 1
                self.current_section_number = 2

        elif chapter_number - 1 != last_chapter.chapter_number:
            self.warn("Chapter number is not sequential."
                      "last chapter number: {}, current chapter number: {}, current_title_line: {}".format(
                        last_chapter.chapter_number, chapter_number, line.strip()))

        last_chapter.content = "\n".join(self.accumulated_text)
        self.accumulated_text = []
        last_chapter.section_number = self.current_section_number
        # print(last_chapter.get_chapter_name())
        self.chapters.append(last_chapter)
        return self

    def consume_normal_line(self, line: str):
        self.accumulated_text.append(line)

    def end(self, novel_name: str) -> Novel:
        self.current_chapter.content = "\n".join(self.accumulated_text)
        self.current_chapter.section_number = self.current_section_number
        self.chapters.append(self.current_chapter)
        return Novel(novel_name, self.foreword, self.chapters)

# below are test code
# def get_files_by_file_size(directory_path, reverse=False):
#     """ Return list of file paths in directory sorted by file size """
#
#     # Get list of files
#     file_paths = []
#     for basename in os.listdir(directory_path):
#         filename = os.path.join(directory_path, basename)
#         if os.path.isfile(filename):
#             file_paths.append(filename)
#
#     # Re-populate list with filename, size tuples
#     for i in range(len(file_paths)):
#         file_paths[i] = (file_paths[i], os.path.getsize(file_paths[i]))
#
#     # Sort list by file size
#     # If reverse=True sort from largest to smallest
#     # If reverse=False sort from smallest to largest
#     file_paths.sort(key=lambda filename: filename[1], reverse=reverse)
#
#     # Re-populate list with just filenames
#     for i in range(len(file_paths)):
#         file_paths[i] = file_paths[i][0]
#
#     return file_paths
#
# def test_file(file_path: str):
#     print(file_path)
#     f = open(file_path, encoding="utf-8")
#     parser = NovelParser()
#     for novel_line in f:
#         parser.parse_line(novel_line)
#     novel = parser.end("abc")
#     for chapters in novel.chapters:
#         print(chapters.get_chapter_name())
#
#
# file_paths = get_files_by_file_size("d:/temp/", True)
#
# test_file(file_paths[2800])