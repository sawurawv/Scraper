# -*- coding: utf-8 -*-
import scrapy


class FundrazrSpider(scrapy.Spider):
    name = 'fundrazr'
    allowed_domains = ['fundrazr.com']
    start_urls = ['https://fundrazr.com/find?category=Health']

    def parse(self, response):
        for news in response.css('div.content'):
            item = {}
            item['Name'] = news.css('h2.title>a::text').extract_first()
            item['Posted By'] = news.css('p')