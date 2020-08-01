# -*- coding: utf-8 -*-
import scrapy
from scrapy import FormRequest, Request
import os

class LearnaboutbeautySpider(scrapy.Spider):
    name = 'learnaboutbeauty'
    allowed_domains = ['learnaboutbeauty.com']
    dirname = 'pdf_files'

    custom_settings = {
        'HTTPCACHE_ENABLED': False
    }

    def start_requests(self):
        if not os.path.isdir(self.dirname):
            os.makedirs(self.dirname)

        yield FormRequest('https://www.learnaboutbeauty.com/eco_login.php', formdata={'action':'login', 'ReturnTo':'', 'txtUserId':'igr@rogers.com', 'txtPassword':'Student1234'}, callback=self.parse_learn)

    def parse_learn(self, response):
        yield Request('https://www.learnaboutbeauty.com/eco_learn.php', callback=self.parse_student)

    def parse_student(self,response):
        yield Request('https://www.learnaboutbeauty.com/eco_session_player.php?id=8008', callback=self.parse_topic)

    def parse_topic(self, response):
        for links in response.css('article.media dl.description>dt>a'):
            link = links.css('::attr(href)').get()
            yield Request(response.urljoin(link), callback=self.parse_links)

    def parse_links(self, response):
        for links in response.css('section#learning_path_container dl.description>dt>a'):
            link = links.css('::attr(href)').get()
            heading = links.css('::text').get()
            yield Request(response.urljoin(link), callback=self.parse_pdf, meta={'heading':heading})

    def parse_pdf(self,response):
        heading = response.meta.get('heading', '').replace('.', '_').replace(' ', '_')
        pdfs = response.xpath('//a[contains(., "Study Slides")]/@href').extract()
        if pdfs:
            for i, pdf in enumerate(pdfs):
                yield Request(response.urljoin(pdf),callback=self.parse_save_pdf, meta= {'heading':heading, 'i': i+1} )

        # if pdf exists
        # heading = heading.replace('.', '_')
        # check if dir name heading exists
        # create if it doesn't
        # then only create directory
        # if it is already not there

    def parse_save_pdf(self,response):
        heading = response.meta.get('heading', '')
        i = response.meta.get('i', 1)

        directory = os.path.join(self.dirname, heading)
        if not os.path.isdir(directory):
            os.makedirs(directory)

        path = os.path.join(self.dirname, heading, f'{heading}_{i}.pdf')
        with open(path, 'wb') as f:
            f.write(response.body)
            print(f'Saved file {heading}.pdf')