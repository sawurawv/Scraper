# -*- coding: utf-8 -*-
import scrapy
from scrapy import Request


class BrainyquoteSpider(scrapy.Spider):
    name = 'brainyquote'
    allowed_domains = ['www.brainyquote.com']
    start_urls = ['https://www.brainyquote.com/topics']

    def parse(self, response):
        for links in response.css('div.col-sm-6 div.bqLn a'):
            category_link = links.css('::attr(href)').get()
            yield Request(response.urljoin(category_link), callback= self.parse_quote_link)

    def parse_quote_link(self, response):
        pass #for links in response.css()