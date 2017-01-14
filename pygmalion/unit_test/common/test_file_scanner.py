import json
from unittest import TestCase

from pygmalion.common.file_scanner import FileInformation, DirectoryInformation, DirectoryInformationEncoder, \
    FileScanner


class TestFileScanner(TestCase):
    def test_json_encoding(self):
        f_1_1 = FileInformation("f-1-1测试", 11)
        f_1_2 = FileInformation("f-1-2", 12)
        d1 = DirectoryInformation("d1", [f_1_1, f_1_2])
        f_2_1 = FileInformation("f-2-1", 21)
        f_2_2 = FileInformation("f-2-2", 22)
        d2 = DirectoryInformation("d2", [f_2_1, f_2_2])
        f_1 = FileInformation("f-1", 1)
        f_2 = FileInformation("f-2", 2)
        d = DirectoryInformation("d", [f_1, f_2], [d1, d2])
        json_str = json.dumps(d, cls=DirectoryInformationEncoder, ensure_ascii=False)
        print(json_str)

    def test_file_scanner(self):
        print(FileScanner("e:\\video", 2).scan())
