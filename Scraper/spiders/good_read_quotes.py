# -*- coding: utf-8 -*-
import scrapy
from scrapy import Request


class GoodReadQuotesSpider(scrapy.Spider):
    name = 'good_read_quotes'
    allowed_domains = ['www.goodreads.com']
    start_urls = ['https://www.goodreads.com/quotes']

    def parse(self, response):
        for quotes in response.css('div.quotes div.quote'):
            item ={}
            item['Quote'] = quotes.css('div.quoteText::text').get()
            item['Author'] = quotes.css('span.authorOrTitle::text').get()
            item['Tags'] =  quotes.css('div.greyText a::text').extract()
            item['Likes'] = quotes.css('a.smallText::text').get()
            item['ImageUrl'] = quotes.css('a.leftAlignedImage>img::attr(src)').get('')
            yield item

            next_page = response.css('a.next_page::attr(href)').get()
            if next_page:
                yield Request(response.urljoin(next_page), callback= self.parse)
