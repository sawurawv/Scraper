# -*- coding: utf-8 -*-
import scrapy


class SeffieldHallamUniversitySpider(scrapy.Spider):
    name = 'seffield_hallam_university'
    allowed_domains = ['shu.rl.talis.com']
    start_urls = ['https://shu.rl.talis.com/subjects/sg-66003.html']

    def parse(self, response):
        item = {}
        item['Faculty'] = response.css('small#pageDescription::text').get().split(':')[-1].strip()
        item['Code'] = response.css('tr#row-id-0 td ::text').extract()[1]
        item['Name'] = response.css('tr#row-id-0 td>a.nodeName::text').get()
        yield item