# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

# import pymysql
import os
from urllib.parse import urlparse
from scrapy import Request
from scrapy.exceptions import DropItem
from scrapy.pipelines.files import FilesPipeline
from instagram_user import settings
import pymysql

class MysqlPipeline():
	def __init__(self, host, database, user, password, port):
		self.host = host
		self.database = database
		self.user = user
		self.password = password
		self.port = port

	@classmethod
	def from_crawler(cls, crawler):
		return cls(
			host=crawler.settings.get('MYSQL_HOST'),
			database=crawler.settings.get('MYSQL_DATABASE'),
			user=crawler.settings.get('MYSQL_USER'),
			password=crawler.settings.get('MYSQL_PASSWORD'),
			port=crawler.settings.get('MYSQL_PORT'),
		)

	def open_spider(self, spider):
		self.db = pymysql.connect(self.host, self.user, self.password, self.database, charset='utf8mb4', port=self.port)
		self.cursor = self.db.cursor()

	def close_spider(self, spider):
		self.db.close()

	def process_item(self, item, spider):
		data = dict(item)
		keys = ', '.join(data.keys())
		values = ', '.join(['%s']*len(data))
		insert_sql = 'insert into %s (%s) values (%s)' % (item['username'], keys, values)
		# update_sql = 'update %s set %s=%s where %s=%s'
		self.cursor.execute(insert_sql, tuple(data.values()))
		self.db.commit()
		return item

class FilePipeline(FilesPipeline):
	def file_path(self, request, response=None, info=None):
		# use the meta store in get_media_requests and get the item
		item = request.meta['item']
		# use username in item to dirct the path
		file_name = item['username'] +'/'+ os.path.basename(urlparse(request.url).path)
		return file_name
	
	def item_completed(self, results, item, info):
		image_paths = [x['path'] for ok, x in results if ok]
		if not image_paths:
			raise DropItem('Image Downloaded Failed')
		return item
	
	def get_media_requests(self, item, info):
		for url in item['image_list'].split(';'):
			if url is not '':
				# Add item with meta into request for following step
				yield Request(url, meta={'item': item})
		for url in item['video_list'].split(';'):
			if url is not '':
				yield Request(url, meta={'item': item})

class InstagramUserPipeline(object):
    def process_item(self, item, spider):
        return item
