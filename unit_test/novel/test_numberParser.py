from unittest import TestCase

from novel.number_parser import ChineseNumberParser


class TestChineseNumberParser(TestCase):

    def test_parse_int(self):
        self.assertEqual(ChineseNumberParser("999").parse_int(), 999)
        self.assertEqual(ChineseNumberParser("一").parse_int(), 1)
        self.assertEqual(ChineseNumberParser("十").parse_int(), 10)
        self.assertEqual(ChineseNumberParser("十一").parse_int(), 11)
        self.assertEqual(ChineseNumberParser("一十一").parse_int(), 11)
        self.assertEqual(ChineseNumberParser("一百").parse_int(), 100)
        self.assertEqual(ChineseNumberParser("一百零一").parse_int(), 101)
        self.assertEqual(ChineseNumberParser("一百一十").parse_int(), 110)
        self.assertEqual(ChineseNumberParser("一百一十一").parse_int(), 111)
        self.assertEqual(ChineseNumberParser("一千").parse_int(), 1000)
        self.assertEqual(ChineseNumberParser("一千零一").parse_int(), 1001)
        self.assertEqual(ChineseNumberParser("一千一百").parse_int(), 1100)
        self.assertEqual(ChineseNumberParser("一千一百一十").parse_int(), 1110)
        self.assertEqual(ChineseNumberParser("一千一百一十一").parse_int(), 1111)
        self.assertEqual(ChineseNumberParser("一万").parse_int(), 10000)
        self.assertEqual(ChineseNumberParser("一万一千").parse_int(), 11000)
        self.assertEqual(ChineseNumberParser("一万一千零一").parse_int(), 11001)
        self.assertEqual(ChineseNumberParser("一万一千一百").parse_int(), 11100)
        self.assertEqual(ChineseNumberParser("一万一千一百一十").parse_int(), 11110)
        self.assertEqual(ChineseNumberParser("一万一千一百一十一").parse_int(), 11111)