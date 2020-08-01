# -*- coding: utf-8 -*-
import scrapy
from scrapy import Request


class BirminghamSpider(scrapy.Spider):
    name = 'birmingham'
    allowed_domains = ['program-and-modules-handbook.bham.ac.uk']
    start_urls = [
        'https://program-and-modules-handbook.bham.ac.uk/webhandbooks/WebHandbooks-control-servlet?Action=getModuleSearchList&pgDspAllOpts=N']

    def start_requests(self):
        levels = ['LC', 'LF', 'LH', 'LI']
        url = 'https://program-and-modules-handbook.bham.ac.uk/webhandbooks/WebHandbooks-control-servlet?Action=getModuleSearchList&pgDspAllOpts=Y'
        for level in levels:
            yield scrapy.FormRequest(url,
                                     formdata={'termTxtSearch': '002019', 'ModTxt': '', 'TitleTxt': '', 'LevTxt': level,
                                               'DeptTxt': ''})

    def parse(self, response):
        for links in response.css('table.whDefaultTab td.whTDText>a'):
            link = links.css('::attr(href)').get()
            yield Request(response.urljoin(link), callback= self.parse_course_details)

    def parse_course_details(self, response):
        item = {}
        item['Department'] = response.xpath('//th[text()="Department"]/following::td[1]/text()').get()
        item['Module Code Short'] = response.xpath('//th[contains(text(), "Module") and contains(text(), "Code")]/following::td[1]/text()').get().strip().split(' ')[0]
        item['Module Code'] = response.xpath('//th[contains(text(), "Module") and contains(text(), "Code")]/following::td[1]/text()').get()
        item['Module Title'] = response.xpath('//th[contains(text(), "Module") and contains(text(), "Title")]/following::td[1]/text()').get()
        item['Description'] = response.xpath('//th[text()="Description"]/following::td[1]/text()').get()
        item['Prerequsite'] = response.xpath('//th[text()="Pre-requisites"]/following::td[1]/text()').get()
        item['Credits'] = response.xpath('//th[text()="Credits"]/following::td[1]/text()').get()
        yield item

