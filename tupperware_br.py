# -*- coding: utf-8 -*-
import json
import re

import scrapy
from scrapy import Request


class TupperwareBrSpider(scrapy.Spider):
    name = 'tupperware_br'
    allowed_domains = ['lojavirtualtupperware.com.br']
    start_urls = ['https://www.lojavirtualtupperware.com.br/produtos']

    def parse(self, response, **kwargs):
        for links in response.css('div.search-single-navigator li a'):
            link = links.css('::attr(href)').get()
            yield Request(response.urljoin(link), self.parse_product_link)

    def parse_product_link(self, response):
        for product_links in response.css('article.j-shelf__item a'):
            product_link = product_links.css('::attr(href)').get()
            yield Request(response.urljoin(product_link), callback=self.parse_detail)

    def parse_detail(self, response):
        item = {}
        item['Product Name'] = response.css('h1.j-product__name div::text').get()
        item['URL'] = response.url

        text = response.xpath('//script[contains(text(), "vtex.events.addData")]//text()').get()
        data = json.loads(re.findall('({.*})\)', text)[0])
        stock = list(data['skuStocks'].values())[0]
        item['In Stock'] = True if stock else False
        item['Regular Price'] = response.css('strong.skuBestPrice::text').get('').split(' ')[-1].replace(',', '.')
        item['Sale Price'] = response.css('strong.skuBestPrice::text').get('').split(' ')[-1].replace(',', '.')
        yield item
