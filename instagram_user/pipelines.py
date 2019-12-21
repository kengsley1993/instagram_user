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

class FilePipeline(FilesPipeline):
	def file_path(self, request, response=None, info=None):
		file_name = settings.USERNAME + '/' + os.path.basename(urlparse(request.url).path)
		return file_name
	
	def item_completed(self, results, item, info):
		image_paths = [x['path'] for ok, x in results if ok]
		if not image_paths:
			raise DropItem('Image Downloaded Failed')
		return item
	
	def get_media_requests(self, item, info):
		for url in item['image_list'].split(';'):
			yield Request(url)
		for url in item['video_list'].split(';'):
			yield Request(url)

class InstagramUserPipeline(object):
    def process_item(self, item, spider):
        return item
