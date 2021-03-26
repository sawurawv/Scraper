# -*- coding: utf-8 -*-
import scrapy
import json


class TupperwareMxSpider(scrapy.Spider):
    name = 'tupperware_mx'
    allowed_domains = ['tuperware.com.mx', 'mybcapps.com']
    start_urls = ['https://services.mybcapps.com/bc-sf-filter/filter?shop=tupperware-mx.myshopify.com&page=1&limit=16']

    def parse(self, response, **kwargs):
        json_data = json.loads(response.text)
        products = json_data.get('products', [])
        for product in products:
            item = {}
            item['Product Name'] = product.get('title')
            item['URL'] = f'https://www.tupperware.com.mx/products/{product.get("handle")}'
            item['In Stock'] = product.get('available')
            item['Sale Price'] = product.get('variants', [{}])[0].get('price')
            item['Regular Price'] = product.get('variants', [{}])[0].get('compare_at_price') or item['Sale Price']
            yield item

        if products:
            page = response.meta.get('page', 1) + 1
            yield scrapy.Request(f'https://services.mybcapps.com/bc-sf-filter/filter?'
                                 f'shop=tupperware-mx.myshopify.com&page={page}&limit=16', meta={'page': page})
