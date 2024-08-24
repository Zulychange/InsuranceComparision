# from scrapy.exporters import JsonItemExporter
# from itemadapter import ItemAdapter
import pymysql
import logging


# useful for handling different item types with a single interface
# from itemadapter import ItemAdapter


class InsuranceselectPipeline:
    def __init__(self):
        pass

    def open_spider(self, spider):
        pass

    def process_item(self, item, spider):
        return item

    def close_spider(self, spider):
        pass


class SynchroDBPipeline(object):
    """
    不同的输入类型要使用不同的数据库，或者需要不同的type

    同步插入数据库
    """

    def __init__(self, host, db, port, user, password):
        self.host = host
        self.db = db
        self.port = port
        self.user = user
        self.password = password
        self.connect = pymysql.connect(host=self.host, user=self.user, passwd=self.password, db=self.db, port=self.port, charset='utf8')
        self.cursor = self.connect.cursor()
        logging.info('数据库连接成功 => %s' + '主机：', self.host + ' 端口:' + self.db)

    @classmethod
    def from_crawler(cls, crawler):
        """
        可以简单理解为创建了一个我没看见在哪里使用的实例！
        访问配置：可以轻松获取 Scrapy 的设置（settings）。
        连接信号：能够注册和处理 Scrapy 的信号（signals）。
        统一初始化：提供一种统一的方式来初始化中间件实例。
        :param crawler:
        :return:
        """
        # 获取数据库的配置
        db_name = crawler.settings.get('DB_SETTINGS')
        db_params = db_name.get('db1')
        # 类似实例化
        return cls(
            host=db_params.get('host'),
            db=db_params.get('db'),
            user=db_params.get('user'),
            password=db_params.get('password'),
            port=db_params.get('port'),
        )

    def process_item(self, item, spider):
        # item类似字典，可以使用get方法
        table_fields = list(item.fields.keys())
        table_name = "Insurance2"

        # 这样写的目的是小心逗号
        values_params = '%s,' * (len(table_fields) - 1) + '%s'
        keys = ', '.join(table_fields)
        values = ['%s' % str(item.get(i, '')) for i in table_fields]
        # sql语句
        insert_sql = 'insert into %s (%s) values (%s)' % (table_name, keys, values_params)
        try:
            self.cursor.execute(insert_sql, tuple(values))
            logging.info("数据插入成功 =>" + '1')
        except Exception as e:
            logging.error('执行sql异常 =>' + str(e))
            pass
        finally:
            self.connect.commit()

        return item

    def close_spider(self, spider):
        self.connect.close()
        self.cursor.close()
