import re


class ChineseNumberParser:

    _NUMBER_TRANSLATE_DICT = str.maketrans(u"０１２３４５６７８９一二三四五六七八九零", "01234567891234567890")

    _UNIT_POSITION_MAP = {u"十": 2, u"百": 3, u"千": 4, u"万": 5, u"亿": 9}

    _UNIT_REGEX = re.compile("[{}]".format("".join(_UNIT_POSITION_MAP.keys())))

    def __init__(self, number_text: str):
        self.number_text = number_text.translate(self._NUMBER_TRANSLATE_DICT)

    def parse_int(self) -> int:
        length = len(self.number_text)
        result = ''
        for index in reversed(range(length)):
            c = self.number_text[index]
            if not self._UNIT_REGEX.match(c):
                result = c + result
                continue
            expected_position = self._UNIT_POSITION_MAP.get(c)
            for i in range(expected_position - len(result) - 1):
                result = '0' + result
            if index == 0:
                result = '1' + result
        return int(result)