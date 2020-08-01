# -*- coding: utf-8 -*-
import scrapy
from scrapy import Request
import json


class NeimanmarcusSpider(scrapy.Spider):
    name = 'neimanmarcus'
    allowed_domains = ['www.neimanmarcus.com']
    start_urls = ['https://www.neimanmarcus.com/service/sitemap.jsp']

    def parse(self, response):
        for links in response.css('div.sitemap-content h3.sitemap-link>a'):
            link = links.css('::attr(href)').get()
            category = links.css('::text').get()
            yield Request(response.urljoin(link), callback=self.parse_product_category, meta={'category': category})

    def parse_product_category(self, response):
        for clothing_category in response.css('ul.left-nav__category li a'):
            category = clothing_category.css('::text').get().strip()
            category_link = clothing_category.css('::attr(href)').get()
            # sub_category = clothing_category.css
            if category != 'Shop by Designer' and 'Featured Designers' and 'Designer Sale' and 'Sale' and 'Premier Designer':
                yield Request(response.urljoin(category_link), meta={'category': category},
                              callback=self.parse_sub_category)

    def parse_sub_category(self, response):
        category = response.meta.get('category')
        for product_links in response.css('div.product-thumbnail__details a'):
            product_link = product_links.css('::attr(href)').get()
            yield Request(response.urljoin(product_link), meta={'category': category}, callback= self.parse_detail)

        next_page = response.css('nav.pagination a.arrow-button--right::attr(href)').get()
        if next_page:
            yield Request(response.urljoin(next_page))


    def parse_detail(self, response):
        category = response.meta.get('category')
        data_text = response.css('script[type="application/ld+json"]::text').get()
        json_data = json.loads(data_text)
        item = {}
        item['handle'] = json_data.get('url').split('/')[-1]
        item['title'] = response.css('meta[property="og:title"]::attr(content)').get()
        item['price'] = float(response.css('meta[property="product:price:amount"]::attr(content)').get())
        item['image'] = response.urljoin(response.css('meta[property="og:url"]::attr(content)').get())
        item['description'] = json_data.get('description')
        item['vendor'] = 'neimanmarcus'
        item['category'] = category
        item['sku'] = json_data.get('offers').get('offers')[0].get('sku').split('u')[-1]
        item['stock'] = response.css('meta[property="og:availability"]::attr(content)').get()
        yield item
