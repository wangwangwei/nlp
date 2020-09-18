import re
import TimeExtraction
import redis


class Extraction(object):

    def __init__(self):
        try:
            self.r = redis.StrictRedis(host='localhost', port=6379, decode_responses=True, charset='UTF-8', encoding='UTF-8')
        except ValueError as err:
            print(err)
        self.info_dict = {}     # 定义实体信息字典
        self.text = ''
        self.te = None   # 定义时间抽取类
        self.re_dict = {}     # 定义抽取字典

    def re_extract(self):
        for key, value in self.re_dict.items():
            try:
                result = re.search(value, self.text, re.I)
            except ValueError as err:
                pass
            if result:
                if key.startswith("re"):
                    self.info_dict["entity"].append({key: result.group(), "type": "正则实体", "score": 1.0})
                elif key.startswith("en"):
                    self.info_dict["entity"].append({key: value.split("|")[0], "type": "枚举实体", "score": 1.0})
                elif key.startswith("in"):
                    self.info_dict["entity"].append({key: value.split("|")[0], "type": "意图实体", "score": 1.0})

    def te_extract(self):
        address = ""
        p_list = []
        a_list = []
        for k, v in self.te.cut_word:
            if v == "nr":
                p_list.append(k)
            elif address != '':
                if v == "ns":
                    address += k
                else:
                    a_list.append(address)
                    address = ''
            elif v == "ns":
                address += k
        if address != '':
            a_list.append(address)
        self.info_dict["entity"].append({"address": ",".join(a_list), "type": "智能分析", "score": 1.0})

        if p_list:
            self.info_dict["entity"].append({"name": ",".join(p_list), "type": "智能分析", "score": 1.0})

        time = ",".join(self.te.time_extract())
        if time:
            self.info_dict["entity"].append({"time": time, "type": "智能分析", "score": 1.0})

    def extraction(self, text):
        self.re_dict = self.r.hgetall("regexHash")
        self.text = text
        self.te = TimeExtraction.TimeExtraction(text)
        self.info_dict["segments"] = self.te.seg
        self.info_dict["entity"] = []
        self.re_extract()
        self.te_extract()
        return self.info_dict















# text = "你好，我是黄飞鸿，处女座，今年35岁，我的手机号码是15665471118，我的邮箱是test@163.com，qq号1105565595，" \
#        "护照号是G28233515，" \
#        "我的身份证号码是340822199809070219，来自江苏南京，邮政编码是123456，" \
#        "帮我预定2023年5月1号上午12点至2023年五月5号晚上8点的房间，苹果，珠峰"
# # text2 = ''
# info = Extraction().extraction(text)
# print(info)
