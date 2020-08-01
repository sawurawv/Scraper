# -*- coding: utf-8 -*-
import json
import scrapy
from scrapy import Request


class AmericanEagleSpider(scrapy.Spider):
    name = 'american_eagle'
    allowed_domains = ['www.ae.com']
    start_urls = ['https://www.ae.com/us/en/sitemap']

    def parse(self, response):
        for links in response.css('li.ember-view>a'):
            link = links.css('::attr(href)').get()
            category = links.css('::text').get()
            yield Request(response.urljoin(link), callback=self.parse_category, meta={'category': category})

    def parse_category(self, response):
        category = response.meta.get('category')
        for links in response.css('div.side-content a.nav-link'):
            link = links.css('::attr(href)').get()
            sub_category = links.css('::text').get()
            yield Request(response.urljoin(link), callback=self.parse_sub_category,
                          meta={'sub_category': sub_category, 'category': category})

    def parse_sub_category(self, response):
        category = response.meta.get('category')
        sub_category = response.meta.get('sub_category')
        for product_types in response.css('ul.ember-view>li.tier-3>a'):
            product_type = product_types.css('::attr(href)').get()
            yield Request(response.urljoin(product_type), callback=self.parse_product_link,
                          meta={'category': category, 'sub_category': sub_category})

    def parse_product_link(self, response):
        category = response.meta.get('category')
        sub_category = response.meta.get('sub_category')
        for products in response.css('div.product-tile a'):
            product = products.css('::attr(href)').get()
            yield Request(response.urljoin(product), callback=self.parse_detail,
                          meta={'category': category, 'sub_category': sub_category})

    def parse_detail(self, response):
        category = response.meta.get('category')
        sub_category = response.meta.get('sub_category')
        data = response.css('script.qa-pdp-schema-org::text').get()
        json_data = json.loads(data)
        item = {}
        item['handle'] = json_data.get('offers')[0].get('url').split('/')[-2]
        item['title'] = response.css('meta[property="og:title"]::attr(content)').get()
        item['price'] = response.css('div.product-list-price::text').get().strip()
        item['image'] = json_data.get('image')
        item['description'] = json_data.get('description')
        item['vendor'] = response.css('meta[property="og:site_name"]::attr(content)').get()
        item['category'] = category.strip()
        item['sub_category'] = sub_category.strip()
        item['sku'] = json_data.get('productID')
        yield item