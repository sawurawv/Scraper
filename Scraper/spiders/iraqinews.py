# -*- coding: utf-8 -*-
import scrapy
from scrapy import Request


class IraqinewsSpider(scrapy.Spider):
    name = 'iraqinews'
    allowed_domains = ['iraqinews.com']
    url = 'https://www.iraqinews.com/page/{}/'

    def start_requests(self):
        for i in range(1, 6):
            yield Request(self.url.format(i))

    def parse(self, response):
        news_xpath = '//h3[contains(@class, "entry-title")]/a/@href'
        for news in response.xpath(news_xpath).extract():
            yield Request(response.urljoin(news), callback=self.parse_news)

    def parse_news(self, response):
        item = {}
        item['url'] = response.url
        item['datePublished'] = response.css('time.entry-date::attr(datetime)').get()
        item['headline'] = response.css('h1.entry-title::text').get('').strip().encode().decode('ascii', errors='ignore')
        item['text'] = ''.join(response.css('div.entry-content p::text').extract()).encode().decode('ascii', errors='ignore')
        item['author'] = response.css('span.entry-author>a>strong::text').get()
        item['image'] = response.urljoin(response.css('figure.wp-caption>a::attr(href)').get())
        item['isBasedOn'] = [response.urljoin(tag) for tag in response.css('div.entry-content a::attr(href)').extract()]
        yield item