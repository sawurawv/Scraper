# -*- coding: utf-8 -*-
import scrapy


class IbdbeautySpider(scrapy.Spider):
    name = 'ibdbeauty'
    allowed_domains = ['ibdbeauty.com']
    start_urls = ['http://www.ibdbeauty.com/FAQs/index.html']

    def parse(self, response):
        for faq in response.css('div.faq_box'):
            item = {}
            item['Question'] = faq.css('div.question::text').extract_first()
            item['Answers'] = faq.css('div.answer::text').extract_first()
            yield item
