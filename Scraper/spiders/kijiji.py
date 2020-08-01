# -*- coding: utf-8 -*-
import scrapy
from scraper_api import ScraperAPIClient
from scrapy import Request

client = ScraperAPIClient('69249606b508b5efbeccb8deec25681e')
result = client.get(
    url='https://www.kijiji.ca/b-travel-trailer-camper/ontario/camper/k0c334l9004?sort=relevancyDesc').text


class KijijiSpider(scrapy.Spider):
    name = 'kijiji'
    allowed_domains = ['www.kijiji.ca']
    start_urls = [client.scrapyGet(
        url='https://www.kijiji.ca/b-travel-trailer-camper/ontario/camper/k0c334l9004?sort=relevancyDesc')]

    def parse(self, response):
        for containers in response.css('div.info-container'):
            item = {}
            item['Title'] = containers.css('div.title>a::text').get().strip()
            item['Price'] = containers.css('div.price::text').get().strip()
            item['Location'] = containers.css('div.location>span::text').get().strip()
            item['Description'] = containers.css('div.description::text').get().strip()
            item['Link'] = response.urljoin(containers.css('div.title>a::attr(href)').get())
            yield item


        next_page = response.css('link[rel="next"]::attr(href)').get()
        if next_page:
            yield Request(response.urljoin(next_page))
