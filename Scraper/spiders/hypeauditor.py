# -*- coding: utf-8 -*-
import scrapy
from scrapy import Request
import json
from datetime import datetime


class HypeauditorSpider(scrapy.Spider):
    name = 'hypeauditor'
    allowed_domains = ['hypeauditor.com']
    start_urls = ['https://hypeauditor.com/top-instagram/']

    def parse(self, response):
        headers = {'x-requested-with': 'XMLHttpRequest',
                    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130Safari / 537.36'}
        for links in response.css('td>a.bloggers-top-report-link::attr(href)'):
            username = links.get().split('/')[2]
            unique_id = links.get().split('fh=')[-1]
            url = 'https://hypeauditor.com/ajax/followersGraph/?username={}&fh={}'
            yield Request (url.format(username, unique_id), headers=headers, callback=self.parse_details, meta= {'username' : username})

    def parse_details(self, response):
        data = json.loads(response.text)
        for info in data.get('followers_count'):
            item = {}
            item['username'] = response.meta.get('username')
            item['date'] = datetime.fromtimestamp(int(info.get('time'))).strftime('%Y-%b-%d')
            item['count'] = info.get('count')
            yield item
