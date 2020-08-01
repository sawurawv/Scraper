# -*- coding: utf-8 -*-
import json
from datetime import date
from urllib.parse import urljoin
import scrapy
from scrapy import Request
import html2text


class EmmabridgewaterSpider(scrapy.Spider):
    name = 'emmabridgewater'
    allowed_domains = ['emmabridgewater.co.uk']
    api_url = 'https://www.emmabridgewater.co.uk/products.json?page={}'
    start_urls = [api_url.format(1)]

    def parse(self, response):
        json_data = json.loads(response.text)
        products = json_data.get('products', [])
        if products:
            page = response.meta.get('page', 1) + 1
            yield Request(self.api_url.format(page), meta={'page': page})

        for product in products:
            item = {}
            item['Name'] = product.get('title')
            item['Description'] = html2text.html2text(product.get('body_html') or '')
            item['Product_url'] = urljoin('https://www.emmabridgewater.co.uk/products/', product.get('handle'))
            item['Crawled_date'] = date.today()
            item['Image_url'] = (product.get('images') or [{}])[0].get('src')
            variants = product.get('variants', [])
            variant = variants[0]
            # for variant in variants:
            variant_item = item.copy()
            variant_item['Product_code'] = variant.get('sku')
            variant_item['Price'] = variant.get('price')
            yield variant_item
