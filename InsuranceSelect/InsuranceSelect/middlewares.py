from scrapy import signals
from InsuranceSelect.settings import MY_USER_AGENT
from InsuranceSelect.settings import PROXY_LIST
# pip install -i https://pypi.douban.com/simple selenium这样安装可以，但是我直接安装不行
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
import random

# useful for handling different item types with a single interface
# from itemadapter import is_item, ItemAdapter


class RandomUserAgent(object):
    # 定义一个中间键类
    # 用户代理
    def process_request(self, request, spider):
        ua = random.choice(MY_USER_AGENT)
        # 设置代理请求头
        request.headers['User-Agent'] = ua


class RandomProxy(object):

    # 代理ip列表不对哈
    def process_request(self, request, spider):
        # 随机取出一个代理ip
        proxy = random.choice(PROXY_LIST)

        request.meta['proxy'] = proxy['ip_port']


class SeleniumDownloadMiddleware(object):
    """
    未完成未启用
    selenium下载中间件
    """
    def __init__(self):
        # options = Options()
        # options.add_experimental_option("detach", True)
        self.driver = webdriver.Chrome(service=Service(r"E:\Users\zz\PycharmProjects\py selenu\chromedriver.exe"))  # options=options)

    def process_request(self, request, spider):
        self.driver.get(request.url)
        time.sleep(1)
        try:
            while True:
                pass
        except Exception as e:
            print(e)


class InsuranceselectSpiderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, or item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Request or item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info("Spider opened: %s" % spider.name)


class InsuranceselectDownloaderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        temp = 'introductionUrl=; Hm_lvt_b7dc461be4b3f1b75d87c1f2c7922b77=1722475525,1723014316,1723171351,1723426223; HMACCOUNT=D50983D0A5B61A2C; Hm_lvt_c66b712e1cd824cd55156dbf5089342b=1722475525,1723014316,1723171351,1723426223; merakApiSessionId=5626001e5119144353529fC5jCZ2Wp8H; Hm_lvt_27ca7fb7008b01737e4fc53e00aa3b35=1722475509,1723014317,1723171351,1723426223; MERAK_DEVICE_ID=eb851910fb0b046b554829ccf36439a5; MERAK_RECALL_ID=4326001e51191443536c2VRdF8dpsJgV; MERAK_SESSIONID_ID=d626001e51191443536c2zjofNwwVHlW; _opportunity=%7B%22promotions%22%3A%5B%7B%22n%22%3A%22t1%22%2C%22cd%22%3A1722475649362%2C%22p%22%3A%22xtogissxetdq8yrj4%22%2C%22c%22%3A%22i627royex7%22%2C%22vt%22%3A%22pay%22%2C%22url%22%3A%22https%3A%2F%2Fwww.huize.com%2F%3Futm_source%3DbaiduPZPC%26p%3Dxtogissxetdq8yrj4%26c%3Di627royex7%22%2C%22ut%22%3A%22baiduPZPC%22%7D%2C%7B%22n%22%3A%22t2%22%2C%22cd%22%3A1722475649357%2C%22p%22%3A%22xtogissxetdq8yrj4%22%2C%22c%22%3A%22i627royex7%22%2C%22vt%22%3A%22pay%22%2C%22url%22%3A%22https%3A%2F%2Fwww.huize.com%2F%3Futm_source%3DbaiduPZPC%26p%3Dxtogissxetdq8yrj4%26c%3Di627royex7%22%2C%22ut%22%3A%22baiduPZPC%22%7D%2C%7B%22n%22%3A%22t3%22%2C%22cd%22%3A1722475507947%2C%22p%22%3A%22xtogissxetdq8yrj4%22%2C%22c%22%3A%22i627royex7%22%2C%22vt%22%3A%22pay%22%2C%22url%22%3A%22https%3A%2F%2Fwww.huize.com%2F%3Futm_source%3DbaiduPZPC%26p%3Dxtogissxetdq8yrj4%26c%3Di627royex7%22%2C%22ut%22%3A%22baiduPZPC%22%7D%5D%2C%22firstVisit%22%3Afalse%2C%22hasSeReHistory%22%3Afalse%2C%22matters%22%3A%5B%5D%2C%22activities%22%3A%5B%5D%2C%22rit%22%3A2%2C%22nst%22%3A%22https%3A%2F%2Fwww.huize.com%2Fapps%2Fcps%2Findex%2Fproduct%2Fdetail%3FprodId%3D103128%26planId%3D106985%22%2C%22cum%22%3A%7B%7D%2C%22lpu%22%3A%22https%3A%2F%2Fwww.huize.com%2F%3Futm_source%3DbaiduPZPC%26p%3Dxtogissxetdq8yrj4%26c%3Di627royex7%22%2C%22se%22%3A%22%22%7D; beidou_jssdk_session_id=1723448750527-8559858-086a1e3aa39427-93648111; SSO-ACCESS-TOKEN=cba4558b-ac82-4480-b3cc-90b28f244758; userId=dt1L6I3aLE8=; acw_tc=2f6a1fc117234488208087795ed8da6be80da55e27a69551576a6030657bed; cgsession_id=1723448750527-8559858-086a1e3aa39427-93648111; click_apstatus=1; loginUtmInfo2021={"ru":"https%3A%2F%2Fwww.huize.com%2Fapps%2Fcps%2Findex%2Fproduct%2Fdetail%3FDProtectPlanId%3D106573%26prodId%3D102923%26planId%3D106573","pru":"https%3A%2F%2Fwww.huize.com%2Fmall%2F86","lpu":"https%3A%2F%2Fwww.huize.com%2F%3Futm_source%3DbaiduPZPC%26p%3Dxtogissxetdq8yrj4%26c%3Di627royex7"}; Hm_lpvt_b7dc461be4b3f1b75d87c1f2c7922b77=1723448828; Hm_lpvt_c66b712e1cd824cd55156dbf5089342b=1723448828; Hm_lpvt_27ca7fb7008b01737e4fc53e00aa3b35=1723448828; hz_p_p_id=3603; hz_p_p_type=%E7%BB%88%E8%BA%AB%E5%AF%BF%E9%99%A9; _qxc_token_=240062a5-53f4-48d9-b827-5e1d6b0f9cbd; Product_History=102923%3A106573%2C103128%3A106985%2C102974%3A106660%2C103134%3A106992%2C103173%3A107066%2C103114%3A106958%2C103084%3A106894%2C1001450%3A1003162%2C102968%3A106652%2C102976%3A106667%2C102874%3A106501%2C103031%3A106781%2C103001%3A106700; MERAK_ENTER_PAGE_TIME=1723448828362; beidoudata2015jssdkcross=%7B%22distinct_id%22%3A%221910b8a71117dc-05601f0d98a4-26001e51-1327104-1910b8a7112135e%22%2C%22first_id%22%3A%221910b8a71117dc-05601f0d98a4-26001e51-1327104-1910b8a7112135e%22%2C%22props%22%3A%7B%22%24search_keyword%22%3A%22%E6%9C%AA%E5%8F%96%E5%88%B0%E5%80%BC%22%2C%22%24latest_traffic_source_type%22%3A%22%E7%9B%B4%E6%8E%A5%E6%B5%81%E9%87%8F%22%2C%22%24latest_search_keyword%22%3A%22%E6%9C%AA%E5%8F%96%E5%88%B0%E5%80%BC_%E7%9B%B4%E6%8E%A5%E6%89%93%E5%BC%80%22%2C%22%24latest_referrer%22%3A%22%22%2C%22%24latest_utm_source%22%3A%22hotsearch%22%2C%22%24latest_utm_medium%22%3A%22app%22%2C%22%24latest_utm_term%22%3A%22xmf5h%22%7D%2C%22session_id%22%3A%22%22%2C%22%24page_visit_id%22%3A%221910b8a71117dc-05601f0d98a4-26001e51-1327104-1910b8a7112135e-1723448828748%22%2C%22%24device_id%22%3A%221910b8a71117dc-05601f0d98a4-26001e51-1327104-1910b8a7112135e%22%2C%22sdk_injection%22%3A%22INJECTED%22%2C%22login_id%22%3A%225390214%22%7D; tfstk=fFOsCTVPClq_N78CmO3FdVpcRw1j4hGPXr_vrEFak1CTDoLRYnywQ-PXdnKhQGHGgEIAvnj4_1pwhZtyWGIV317bMnLRXIuG0sGXx1BDQiSNcsTDV2orab8MSsfK40lyR81j2sjxgseEVRiGM0orTb8MSsfv3yUL8A8dxZNT6sKAvJQ5vNFTMnIdpaQzXsCvDe3CojpxAwD1XFgKN1x1Z_sJWMLw7BQ_4gLOASFxuN6sLFIQMSdpKqVoOGHu8ifNjFQ6mbVG6t9v_6dtvjCJEHOfe_MqSOLXdnfw9qeO2d-N3CXQXRQ51G6J69lSJ6XvdB1w6m2k8esOF6JEKcWV1h9lqOHnxnTCbnd1pliF0L8e69t-YWtchKdN9CnKNguQagZSi-aCES_C42gQn-7cnjqIzneJxOQh8QuIRlwcBwbC42gQn-XO-wRrR2Z_n; JSESSIONID=8044A2DB898F9445DFA556E4EB13CC15'
        cookies = {data.split('=')[0]: data.split("=")[-1] for data in temp.split('; ')}

        request.cookies = cookies

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info("Spider opened: %s" % spider.name)
