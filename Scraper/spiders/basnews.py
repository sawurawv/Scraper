# -*- coding: utf-8 -*-
import scrapy
from scrapy import Request


class BasnewsSpider(scrapy.Spider):
    name = 'basnews'
    allowed_domains = ['basnews.com']
    start_urls = ['http://www.basnews.com/index.php/en/news/iraq']

    def parse(self, response):
        for links in response.xpath('//h3[contains(@class, "catItemTitle")]/a'):
            link = links.css('::attr(href)').extract_first()
            yield Request(response.urljoin(link), callback=self.parse_news)

        next_page = response.css('li>a.next::attr(href)').get()
        if next_page:
                start = int(next_page.rsplit('start=', 1)[1])
                if start <=45:
                    yield Request(response.urljoin(next_page))

    def parse_news(self,response):
        item = {}
        item['url'] = response.url
        item['datePublished'] = response.css('span.itemDateCreated::text').get().strip()
        item['headline'] = response.css('h2.itemTitle::text').get('').strip()
        item['text'] = ''.join(response.css('div.itemFullText p span::text').extract()).encode().decode('ascii', errors='ignore')
        item['author'] = response.css('span.itemAuthor a::text').get()
        item['image'] = response.urljoin(response.css('span.itemImage>a::attr(href)').get())
        item['isBasedOn'] = [response.urljoin(tag) for tag in response.css('div.entry-content a::attr(href)').extract()]
        yield item