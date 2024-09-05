# 年金险比较程序
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from scrapy import cmdline
from InsuranceSelect.settings import DB_SETTINGS
from InsuranceSelect.items import InsuranceselectItem
from datetime import datetime
import logging
import pymysql
import requests
import re

inforitemeng = ['vesterSex', 'vesterAge', 'insureForSelf', 'insurantDate', 'sex',
                'insurantDateLimit', 'paymentType', 'insureAgeLimit',
                'receivingWay', 'receivingTime', 'premium']
# 计数变量
count = 1

# 无风险利率
rf = 0.03

# 构造不存在于输入变量的tag集合，否则赋值一次就不改了
ultradict = set()


class GetInformation:
  
    @staticmethod
    def get_validinfor(prompt, pattern):
        """
        得到有效用户输入
        :param prompt:
        :param pattern:
        :return:
        """
        while True:
            value = input(f"{prompt}")
            if re.match(pattern, value):
                break
            else:
                print("！！输入格式错误！！")
        return value

    def get_information(self):
        """
        个人信息基本输入
        """
        print("6号爬虫的信息输入")
        infordict = {}
        infordict['vesterAge'] = self.get_validinfor("请输入投保人生日(xxxx-x-x):", '((19[0-9][0-9]|20[0-9][0-9])-(1[0-2]|0[1-9])-(0[1-9]|[1-2][0-9]|3[0-1]))$')
        infordict['vesterSex'] = self.get_validinfor("请输入投保人性别:", '(男|女)$')
        infordict['insureForSelf'] = self.get_validinfor("是否为自己承保:", '(是|否)$')
        if infordict['insureForSelf'] == "是":
            infordict['insurantDate'] = infordict['vesterAge']
            infordict['sex'] = infordict['vesterSex']
        else:
            infordict['insurantDate'] = self.get_validinfor("被保险人生日:", '(19[0-9][0-9]|20[0-9][0-9])-(1[0-2]|0[1-9])-(0[1-9]|[1-2][0-9]|3[0-1])$')
            infordict['sex'] = self.get_validinfor("请输入被保险人性别:", '(男|女)$')

        infordict['paymentType'] = self.get_validinfor("缴费方式(年交/一次性):", "(年交|一次性)$")
        if infordict["paymentType"] == "一次性":
            infordict['insureAgeLimit'] = "趸交"
        else:
            infordict['insureAgeLimit'] = self.get_validinfor("缴费期限(数字):", "\\d+$")
        # infordict['insurantJob']    = '1-6类'
        infordict['receivingWay'] = self.get_validinfor("领取方式(月领/年领):", "(月领|年领)$")
        infordict['receivingTime'] = self.get_validinfor("领取时间(数字):", '\\d+$')
        infordict['insurantDateLimit'] = self.get_validinfor("保险期限:", "(终身|\\d+)$")
        infordict['premium'] = self.get_validinfor("期望保费:", '\\d+$')
        # infordict['insurePlan'] = "方案一"
        return infordict
         
    @staticmethod
    def generatetype(**infordict):
        """
        生成不同的type数字
        :param infordict:
        :return:
        """
        typenum = ' '
        mapping = {
            # 有限的映射
            "vesterSex": {"男": "1", "女": "0"},
            "sex": {"男": "1", "女": "0"},
            "paymentType": {"年交": "1", "一次性": "0"},
            "receivingWay": {"月领": "1", "年领": "0"},
        }

        def convert_value(tag, value):
            if tag in mapping:
                if value in mapping[tag]:
                    return mapping[tag][value]
            elif tag == 'vesterAge' or tag == 'insurantDate':
                current = datetime.now()
                value = float(current.year) - float(value[:4])
                return int(value)

            elif tag == 'insureAgeLimit':
                if value == '趸交':
                    value = 1
                return value

            elif tag == 'insurantDateLimit':
                if value == '终身':
                    value = 0
                return value

            else:
                return value

        # 转换原始字典中的值
        converted_dict = {key: convert_value(key, value) for key, value in infordict.items()}

        converted_dict.pop("insureForSelf")
        for value in converted_dict.values():
            typenum = typenum + str(value)

        return typenum


class GetandAssemble:
    @staticmethod
    def geturl(url, pagetags):
        """
        组装url，获得对应的参数的保费的url
        :param url:
        :param pagetags:
        :return:
        """
        urltail = []
        url = re.sub('DProtectPlanId=.*?&', '', url)

        prodid_regex = r"prodId=(\d+)"
        planid_regex = r"planId=(\d+)"

        prodid_match = re.search(prodid_regex, url)
        planid_match = re.search(planid_regex, url)

        prodid = prodid_match.group(1) if prodid_match else None
        planid = planid_match.group(1) if planid_match else None
        url = url + '&restrictGeneParams='+'{' + '"productId"%3A"{}"%2C"productPlanId"%3A"{}"%2C"genes"%3A'.format(prodid, planid)
        i = 1

        niandata = ['insureAgeLimit', 'insurantDateLimit']
        suidata = ['receivingTime']  # insurantDateLimit偶尔也要加岁
        for pagetag in pagetags:
            tag_value = Inspider6Spider.infordict[pagetag]
            if pagetag in niandata and (re.match(r'\d+', tag_value)):
                tag_value = tag_value+'年'
            elif pagetag in suidata and (re.match(r'\d+', tag_value)):
                tag_value = tag_value+'岁'
            urltail.append(f'{{"sort"%3A{i}%2C"protectItemId"%3A""%2C"key"%3A"{pagetag}"%2C"value"%3A"{tag_value}"}}%2C')
            i += 1
        url = url + '['+''.join(urltail)+']'+'}'
        url = re.sub('detail', 'tryTrial', url)
        url = re.sub('%2C]', ']', url)
        url = re.sub('/index', '', url)
        # print("组装的url是{}\n".format(url))
        # print()
        return url

    @staticmethod
    def getoptionurl(url):
        """
        获取有表单信息的url
        :param url:
        :return:
        """

        url = re.sub('DProtectPlanId=.*?&', '', url)
        url = re.sub('detail', 'getTrial', url)
        url = re.sub('/index', '', url)
        return url

    @staticmethod
    def tag_value(tag, i, j):
        """
        判断标签的数值
        :param tag:
        :param i:
        :param j: 判断是范围还是取值
        :return:  tag_value
        """
        global ultradict
        if (tag in Inspider6Spider.infordict) and (tag not in ultradict):
            tag_value = Inspider6Spider.infordict[tag]

        elif j == 1:
            # 给没输入的值赋一个默认合法的值；
            Inspider6Spider.infordict[tag] = i['dictionaryList'][0]['value']
            tag_value = Inspider6Spider.infordict[tag]
            ultradict.add(tag)
            print("{}默认取值{}".format(tag, tag_value))

        elif j == 2:
            Inspider6Spider.infordict[tag] = i['dictionaryList'][0]['min']
            tag_value = Inspider6Spider.infordict[tag]
            ultradict.add(tag)
            print("{}默认取值{}".format(tag, tag_value))

        else:
            tag_value = 0
        return tag_value

    @staticmethod
    def synpool(tag, sample_space):
        """
        解决同义不同形式问题，构建同义池
        :param tag:
        :param sample_space:
        :return:
        """
        if tag == "insurantDateLimit":
            if "终身" in sample_space:
                sample_space.append("至106")
            elif "至106" in sample_space:
                sample_space.append("终身")

        return sample_space

    @staticmethod
    def get_premium(isyear, wantyear, premium):
        """
        将基本保险金额转为与领取方式相匹配的每期领取金额
        :param isyear:
        :param wantyear:
        :param premium:
        :return:
        """
        # 先转为年基本保险金额
        premium = float(premium)
        if not isyear:
            # 合同中的计算系数，差别不大
            premium = premium * 11.813

        if wantyear:
            print(f"年领金额 is {premium}")
        else:
            # 合同中系数，很统一
            premium = premium * 0.085
            print(f"月领金额 is {premium}")
        return premium

    @staticmethod
    def get_pv(premium, wantyear):
        """
        计算能领取保险金的现值
        :return:
        """
        # 第四套生命表，男寿命84，女寿命90
        start_time = float(Inspider6Spider.infordict['receivingTime'])
        end_time = Inspider6Spider.infordict['insurantDateLimit']
        born_time = Inspider6Spider.infordict['insurantDate']
        current = datetime.now()
        age = float(current.year) - float(born_time[:4])
        if end_time == "终身":
            if wantyear:
                # 按年计算

                if Inspider6Spider.infordict['sex'] == "男":
                    period = 84 - start_time
                else:
                    period = 90 - start_time
                pv_1 = premium * (1 - (1 / (1 + 0.03)) ** period) / (1 - (1 / (1 + 0.03)))

            else:
                if Inspider6Spider.infordict['sex'] == "男":
                    period = (84 - start_time)*12
                else:
                    period = (90 - start_time)*12
                pv_1 = premium * (1 - (1 / (1 + 0.00247)) ** period) / (1 - (1 / (1 + 0.00247)))
        else:
            period = float(end_time)
            if wantyear:
                # 按年计算
                pv_1 = premium * (1 - (1 / (1 + 0.03)) ** period) / (1 - (1 / (1 + 0.03)))

            else:
                pv_1 = premium * (1 - (1 / (1 + 0.00247)) ** period) / (1 - (1 / (1 + 0.00247)))

        pv = pv_1 * (1 / (1 + 0.03)) ** (start_time-age)
        return pv

    @staticmethod
    def getpagetags(url):
        """
        获取页面全部的表单数据
        return:      restrict_data:字典信息
                        pagetags:存在的元素
        """
        option_url = GetandAssemble.getoptionurl(url)
        headers1 = {
            'User-Agent': '自己的agent',
        }
        response = requests.get(option_url, headers=headers1)
        json_data = response.json()
        restrict_data = json_data['data']["restrictGenes"]
        description_data = json_data['data']['protectTrialItemList']

        pagetags = []
        for i in restrict_data:
            if "key" in i:
                pagetags.append(i['key'])
        return restrict_data, pagetags, description_data

    @staticmethod
    def filter_option(restrict_data):
        """
        判断输入信息是否符合保单要求
        给未输入信息赋予合法数值

        :param restrict_data: 数据
        :return:        是否保留这个保险（a=1：是；a=0否）
        """
        global ultradict
        # 范围的数据有："insurantDate"、'vesterAge'、 "premium"
        rangedata = ['insurantDate', 'vesterAge', 'premium']
        a = None
        for i in restrict_data:
            if ('key' in i) and (i['key'] not in rangedata):
                tag = i['key']

                tag_value = GetandAssemble.tag_value(tag, i, 1)

                sample_space = [j['value'] for j in i["dictionaryList"]]
                sample_space = GetandAssemble.synpool(tag, sample_space)
                if tag_value not in sample_space:
                    # 写出不符合原因
                    print("值是{},样本空间是{}".format(tag_value, sample_space))
                    a = 0  # 判断变量
                    break
                else:
                    a = 1
                    continue

            elif ('key' in i) and (i['key'] in rangedata):
                tag = i['key']

                tag_value = GetandAssemble.tag_value(tag, i, 2)

                # 处理时间
                if re.match(r'\d{4}-\d{2}.*', tag_value):
                    current = datetime.now()
                    tag_value = float(current.year) - float(tag_value[:4])

                min_i = i["dictionaryList"][0]['min']
                max_i = i["dictionaryList"][0]['max']
                if float(max_i) < float(tag_value) or float(tag_value) < float(min_i):
                    print("值是{}，最小值{}，最大值{}".format(tag_value, min_i, max_i))
                    a = 0  # 判断变量
                    break
                else:
                    a = 1
                    continue

        return a


class Inspider6Spider(CrawlSpider):

    name = "Inspider6"
    allowed_domains = ["huize.com"]

    start_urls = [f"https://www.huize.com/mall/5/{i}" for i in range(1, 18)]
    # start_urls = [f"https://www.huize.com/mall/86/{i}" for i in range(1, 3)]
    # start_urls = [f"https://www.huize.com/mall/86/1"]

    gi = GetInformation()
    infordict = gi.get_information()
    typenum = gi.generatetype(**infordict)

    rules = [Rule(LinkExtractor(allow=r'^(https://www.huize.com/apps/cps/index/product/detail?).*'), callback='parse_times', follow=True)]

    def __init__(self, *args, **kwargs):
        super(Inspider6Spider, self).__init__(*args, **kwargs)
        db_params = DB_SETTINGS.get('db1')
        self.connect = pymysql.connect(host=db_params.get('host'), user=db_params.get('user'), passwd=db_params.get('password'), db=db_params.get('db'),
                                        port=db_params.get('port'), charset='utf8')
        self.cursor = self.connect.cursor()
        logging.info('<<<<数据库连接成功>>>>')

    def parse_times(self, response):
        """
        count为爬取的年金保险数量
        :param response:
        :return:
        """
        global count

        url = response.url
        name = response.xpath('//*[@id="detialtab"]/div/div[1]/h1/text()').extract_first()
        company = response.xpath('//*[@id="detialtab"]/div/div[1]/a[4]/text()').extract_first()

        if "年金" in name:
            print(f"{count}、")
            print('URL is :{}'.format(url))
            print('name is :{}'.format(name))
            print('company is :{}'.format(company))
            # 判断存在哪些元素
            restrict_data, pagetags, description_data = GetandAssemble.getpagetags(url)

            judgea = GetandAssemble.filter_option(restrict_data)

            isyear = description_data[1]["description"]
            if ("0.085" in isyear) or ("8.5%" in isyear) or ("8.45%" in isyear):
                # 判断基本保险金额按年还是月给付
                isyear = 1
            else:
                isyear = 0
            if self.infordict['receivingWay'] == "年领":
                # 判断想要月付还是年付
                wantyear = 1
            else:
                wantyear = 0

            select_sql = "SELECT * FROM insurance2 WHERE name = %s and type = %s"
            self.cursor.execute(select_sql, (name, Inspider6Spider.typenum, ))
            result = self.cursor.fetchone()

            if judgea and (not result):

                new_url = GetandAssemble.geturl(url, pagetags)

                try:
                    headers1 = {
                        'User-Agent': '自己的agent',
                    }
                    response = requests.get(new_url, headers=headers1)
                    # print("进去找找数据{}".format(new_url))
                    json_data = response.json()
                    premium = json_data['data']['protectTrialItemList'][0]["fullPremium"]

                    premium = GetandAssemble.get_premium(isyear, wantyear, premium)
                    pv = GetandAssemble.get_pv(premium, wantyear)
                    print(f"年金现值 is {pv}")
                    print()

                    inItem = InsuranceselectItem(
                        name=name,
                        company=company,
                        sex=Inspider6Spider.infordict['sex'],
                        premium=Inspider6Spider.infordict['premium'],
                        url=url,
                        sum_assured=premium,
                        pv=pv,
                        type=Inspider6Spider.typenum,

                    )
                    yield inItem
                except Exception as e:

                    print(f"出了{e}问题")

                finally:
                    count += 1
            else:
                count += 1
                print(r'{}不符合要求/已经获得'.format(name))
                print()

        else:
            print("{}为非年金保险".format(name))

    def close(self, spider, reason):
        print(f"{spider.name}因为{reason}原因关闭")
        print(f"抓取了{count-1}个年金保险")
        print()
        sql_2 = "SELECT name, pv, url FROM insurance2 Where type = %s ORDER BY pv DESC LIMIT 3"
        self.cursor.execute(sql_2, (Inspider6Spider.typenum, ))
        result = self.cursor.fetchall()

        i = 1
        print("最推荐的三款保险如下")
        for row in result:
            name, pv, url = row
            print("{}、您的条件下{}的现值为{}: {}".format(i, name, pv, url))
            i += 1


# cmdline.execute('scrapy crawl Inspider5'.split())
