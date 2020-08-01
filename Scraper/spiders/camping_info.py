# -*- coding: utf-8 -*-
import scrapy
from scrapy import Request


class CampingInfoSpider(scrapy.Spider):
    name = 'camping_info'
    allowed_domains = ['en.camping.info']
    start_urls = ['https://en.camping.info/campsites']

    def parse(self, response):
        for links in response.css('h2.s651>a'):
            link = links.css('::attr(href)').get()
            yield Request(response.urljoin(link), callback=self.parse_detail)

    def parse_detail(self, response):
        pass
