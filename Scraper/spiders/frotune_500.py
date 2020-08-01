# -*- coding: utf-8 -*-
import scrapy


class Frotune500Spider(scrapy.Spider):
    name = 'frotune_500'
    allowed_domains = ['fortune.com']
    start_urls = ['http://fortune.com/']

    def parse(self, response):
        pass
