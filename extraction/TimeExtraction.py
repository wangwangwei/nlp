# coding=utf-8
import datetime
import re
import jieba.posseg as psg
import jieba
from dateutil import parser  # 日期相关库里的一个日期解析器 能够将字符串 转换为日期格式


class TimeExtraction(object):
    """
    时间抽取
    """
    def __init__(self, text):
        self.cut_word = [(x.word, x.flag) for x in psg.cut(text)]
        self.seg = jieba.lcut(re.sub(r"[\s+\.\!\/_,$%^*()?;；:-【】+\"\']+|[+——！，;:。？、~@#￥%……&*（）]+", "", text))
        self.UTIL_CN_NUM = {
            '零': 0, '一': 1, '二': 2, '两': 2, '三': 3, '四': 4,
            '五': 5, '六': 6, '七': 7, '八': 8, '九': 9,
            '0': 0, '1': 1, '2': 2, '3': 3, '4': 4,
            '5': 5, '6': 6, '7': 7, '8': 8, '9': 9
        }
        self.UTIL_CN_UNIT = {'十': 10, '百': 100, '千': 1000, '万': 10000}

    def check_time_valid(self, word):
        """
        检查抽取的日期有效性
        """
        m = re.match(r"\d+$", word)
        if m:
            if len(word) <= 6:
                return None
        # word1 = re.sub(r'[号,日]\d+$', '日', word)
        word1 = word.replace("号", "日")
        if len(re.findall("日", word1)) > 1:
            return None
        elif word1 != word:
            return self.check_time_valid(word1)
        else:
            return word1

    def cn2dig(self, src):
        if src == "":
            return None
        m = re.match(r"\d+", src)
        if m:
            return int(m.group())
        rsl = 0
        unit = 1
        for item in src[::-1]:
            if item in self.UTIL_CN_UNIT.keys():
                unit = self.UTIL_CN_UNIT[item]
            elif item in self.UTIL_CN_NUM.keys():
                num = self.UTIL_CN_NUM[item]
                rsl += num * unit
            else:
                return None
        if rsl < unit:
            rsl += unit
        return rsl

    def year2dig(self, year):
        res = ''
        for item in year:
            if item in self.UTIL_CN_NUM.keys():
                res = res + str(self.UTIL_CN_NUM[item])
            else:
                res = res + item
        m = re.match(r"\d+", res)
        if m:
            if len(m.group()) == 2:
                return int(datetime.datetime.today().year // 100) * 100 + int(m.group())
            else:
                return int(m.group())
        else:
            return None

    def parse_datetime(self, msg):
        if msg is None or len(msg) == 0:
            return None
        # try:
        #     dt = parser.parse(msg)
        #     if dt.year < 1900:
        #         return None
        #     return dt.strftime('%Y-%m-%d %H:%M:%S')
        # except:
        m = re.match(
            r"([0-9零一二两三四五六七八九十]+年)?([0-9一二两三四五六七八九十]+月)?"
            r"([0-9一二两三四五六七八九十]+[日号])?([上中下午晚早]+)?"
            r"([0-9零一二两三四五六七八九十百]+[点时])?([0-9零一二三四五六七八九十百]+分)?"
            r"([0-9零一二三四五六七八九十百]+秒)?", msg)

        if m.group():
            res = {
                "year": m.group(1),
                "month": m.group(2),
                "day": m.group(3),
                "hour": m.group(5) if m.group(5) is not None else '00',
                "minute": m.group(6) if m.group(6) is not None else '00',
                "second": m.group(7) if m.group(7) is not None else '00',
            }

            params = {}
            for name in res:
                if res[name] is not None and len(res[name]) != 0:
                    tmp = None
                    if name == 'year':
                        tmp = self.year2dig(res[name][:-1])
                        params[name] = int(tmp)
                    else:
                        tmp = self.cn2dig(res[name][:-1])
                        params[name] = int(tmp)
            try:
                target_date = datetime.datetime.today().replace(**params)  # 替换给定日期，但不改变原日期
            except ValueError as err:
                return None
            is_pm = m.group(4)
            if is_pm is not None:
                if is_pm == u'下午' or is_pm == u'晚上' or is_pm == U'中午':
                    hour = target_date.time().hour
                    if hour < 12:
                        target_date = target_date.replace(hour=hour + 12)

            return target_date.strftime('%Y-%m-%d %H:%M:%S')
        else:
            return None

    def time_extract(self):
        """
        启动函数
        :param text:
        :return:
        """

        time_res = []
        address = ''
        word = ''
        key_date = {'今天': 0, '明天': 1, '后天': 2, '昨天': -1, '前天': -2, '明晚': 1, "昨晚": -1}
        for k, v in self.cut_word:  # k是切分的词，v是对应词的词性
            if k in key_date:
                if word != '':
                    time_res.append(word)
                word = (datetime.datetime.today() + datetime.timedelta(days=key_date.get(k, 0))).strftime(
                    '%Y{y}%m{m}%d{d}').format(y='年', m='月', d='日')
                if k == "明晚" or "昨晚":
                    word = (datetime.datetime.today() + datetime.timedelta(days=key_date.get(k, 0))).strftime(
                        '%Y{y}%m{m}%d{d}').format(y='年', m='月', d='日') + "晚上"
            elif word != '':
                if v in ['m', 't']:
                    word += k
                else:
                    time_res.append(word)
                    word = ''

            elif v in ['m', 't']:
                word = k
        if word != '':
            time_res.append(word)

        result = list(filter(lambda x: x is not None, [self.check_time_valid(w) for w in time_res]))
        final_res = [self.parse_datetime(w) for w in result]
        return [x for x in final_res if x is not None]




