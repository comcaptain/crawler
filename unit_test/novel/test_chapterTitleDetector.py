from unittest import TestCase

from novel.chapter_title_detector import ChapterTitleDetector


class TestChapterTitleDetector(TestCase):

    def setUp(self):
        self.detector = ChapterTitleDetector()

    def test_detect_chapter_title(self):
        detector = self.detector
        self.assertEqual(detector.detect_chapter_title(''), None)
        self.assertEqual(detector.detect_chapter_title(u'　　门后面是一张桌子，准确地说是一张插满了各式各样军刀的桌子。'), None)
        self.assertEqual(detector.detect_chapter_title(u'我第一章花了半个小时'), None)
        self.assertEqual(detector.detect_chapter_title(u'　　第二回　合，是我在在竞技场和两个兽人比赛，他们两眼泛着红光，看上去'), None)
        self.assertEqual(detector.detect_chapter_title(u'第一'), None)
        self.assertEqual(detector.detect_chapter_title(u'　　（万一那两个小鬼真的有事，那我该怎么办？该动手做些什么吗？）'), None)

        chapter = self.detector.detect_chapter_title(u'第五卷 第一百一十一章 法师　')
        self.assertEqual(chapter.chapter_name, u'法师')
        self.assertEqual(chapter.chapter_number, 111)

        chapter = self.detector.detect_chapter_title(u'第五卷 第一百一十一节 法师　')
        self.assertEqual(chapter.chapter_name, u'法师')
        self.assertEqual(chapter.chapter_number, 111)

        chapter = self.detector.detect_chapter_title(u'第五卷 第一百一十一话 法师　')
        self.assertEqual(chapter.chapter_name, u'法师')
        self.assertEqual(chapter.chapter_number, 111)

        chapter = self.detector.detect_chapter_title(u'　　　　　　　　　　　　　第一章  蒂蕾初折')
        self.assertEqual(chapter.chapter_name, u'蒂蕾初折')
        self.assertEqual(chapter.chapter_number, 1)

        chapter = self.detector.detect_chapter_title(u'　　　　　　　　第十六集　诡谲政局　第０１章　脱胎换骨')
        self.assertEqual(chapter.chapter_name, u'脱胎换骨')
        self.assertEqual(chapter.chapter_number, 1)

        chapter = self.detector.detect_chapter_title(u'　　　　　　　　　　　　　　　６５－３')
        self.assertEqual(chapter.chapter_name, '')
        self.assertEqual(chapter.chapter_number, 3)

        chapter = self.detector.detect_chapter_title(u'　　　　　　　　　　　　　　　１６—１')
        self.assertEqual(chapter.chapter_name, '')
        self.assertEqual(chapter.chapter_number, 1)

    def test_full_width_space(self):
        # 全角空格测试
        chapter = self.detector.detect_chapter_title(u'　第一回 法师　')
        self.assertEqual(chapter.chapter_name, u'法师')
        self.assertEqual(chapter.chapter_number, 1)

    def test_full_width_parenthesis_chapter_title(self):
        # tab测试，全角括号测试
        chapter = self.detector.detect_chapter_title(u'　     （１２） 法师 涅槃')
        self.assertEqual(chapter.chapter_name, u'法师 涅槃')
        self.assertEqual(chapter.chapter_number, 12)

    def test_half_width_parenthesis_chapter_title(self):
        # 集测试，半角括号测试
        chapter = self.detector.detect_chapter_title(u'第3集(一万一千一百零一) 法师')
        self.assertEqual(chapter.chapter_name, u'法师')
        self.assertEqual(chapter.chapter_number, 11101)
        chapter = self.detector.detect_chapter_title(u'第34集 (１２) 法师')
        self.assertEqual(chapter.chapter_name, u'法师')
        self.assertEqual(chapter.chapter_number, 12)
