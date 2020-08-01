# -*- coding: utf-8 -*-
import scrapy
from scrapy import Request


class AaSpider(scrapy.Spider):
    name = 'aa'
    allowed_domains = ['aa.com.tr']
    start_urls = ['http://aa.com.tr/']

    def parse(self, response):
        for links in response.xpath('//div[contains(@class , "konu-alt-yazi")]/a'):
            link = links.css('::attr(href)').get()
            yield Request(response.urljoin(link), callback=self.parse_news)



    def parse_news(self,response):
        item = {}
        item['url'] = response.url
        item['datePublished'] = response.css('div.item-date::text').get().split('\r')[1].strip()
        item['headline'] = response.css('h2.page-header::text').get('').strip().encode().decode('ascii',
                                                                                                errors='ignore')
        item['text'] = ''.join(
            response.xpath('//div[contains(@class, "item-text")]/descendant::text()').extract()).encode().decode(
            'ascii', errors='ignore')
        item['author'] = ''
        item['image'] = response.urljoin(response.css('figure.item-image img::attr(src)').get())
        item['isBasedOn'] = [response.urljoin(tag) for tag in response.css('div.entry-content a::attr(href)').extract()]
        yield item