# -*- coding: utf-8 -*-
import scrapy
import re

class LeedsAcUkSpider(scrapy.Spider):
    name = 'leeds_ac_uk'
    allowed_domains = ['webprod3.leeds.ac.uk']
    start_urls = ['http://webprod3.leeds.ac.uk/catalogue/dynmodules.asp?Y=201920&M=ANAT-3105']

    def parse(self, response):
        item = {}
        item['Subject'] = response.css('div#module-programmes h2::text').get().split()[-1]
        item['Subject short'] = response.css('div#module-programmes h2::text').get().split()[0].split('3')[0]
        item['Subject code1'] = response.css('div#module-programmes h2::text').get().split()[0]
        item['Topic'] = response.css('div#module-programmes h2::text').get().split('\n')[-1]
        Syllabus = response.css('div#module-programmes')