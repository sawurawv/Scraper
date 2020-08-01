# -*- coding: utf-8 -*-
import json
from urllib.parse import urljoin

import scrapy
from bs4 import BeautifulSoup

from scrapy import Request


class BeerScraperSpider(scrapy.Spider):
    name = 'beer_scraper'
    allowed_domains = ['beeradvocate.com', 'ratebeer.com', 'untappd.com']
    custom_settings = {
        'FEED_EXPORT_FIELDS': ['beer', 'beeradvocate_score', 'beeradvocate_style', 'beeradvocate_abv', 'ratebeer_score',
                               'untappd_abv', 'untappd_ibu', 'untappd_rating'],
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.122 Safari/537.36',
        'DOWNLOAD_DELAY': 1,
        'CONCURRENT_REQUESTS': 4,
        'HTTPCACHE_ENABLED': True,
        'HTTPCACHE_EXPIRATION_SECS': 0,
        'HTTPCACHE_DIR': 'httpcache',
        'HTTPCACHE_IGNORE_HTTP_CODES': [400, 401, 403, 404, 405, 407, 415, 429, 500, 501, 503, 504],
        'HTTPCACHE_STORAGE': 'scrapy.extensions.httpcache.FilesystemCacheStorage'
    }

    def start_requests(self):
        with open('beer.csv') as file:
            beers = file.read().split('\n')
            for beer in beers:
                yield Request(f'https://www.beeradvocate.com/search/?q={beer}', meta={'beer': beer})

    def parse(self, response):
        beer = response.meta.get('beer')
        item = {}
        item['beer'] = beer
        if 'beer/profile/' in response.url:
            soup = BeautifulSoup(response.text, 'html.parser')
            item['beeradvocate_score'] = soup.select_one(
                'div#score_box').text.split('SCORE', 1)[1].strip().split('\n', 1)[0]
            item['beeradvocate_style'] = soup.select('dd.beerstats b')[0].text
            item['beeradvocate_abv'] = soup.select('dd.beerstats b')[1].text
        else:
            first = response.xpath('//div[@id="ba-content"]//a[contains(@href, "/beer/profile/")]/@href').get()
            if first:
                yield Request(urljoin('https://www.beeradvocate.com/', first), meta={'beer': beer})

        ratebeer_url = f'https://beta.ratebeer.com/v1/api/graphql/?operationName=SearchResultsBeer&variables=%7B%22query%22%3A%22{beer}%22%2C%22order%22%3A%22MATCH%22%2C%22includePurchaseOptions%22%3Atrue%2C%22latlng%22%3A%5B39.99266815185547%2C-75.1415023803711%5D%7D&extensions=%7B%22persistedQuery%22%3A%7B%22version%22%3A1%2C%22sha256Hash%22%3A%22258a594a313dd904fa6cc92ba6a1387c66af7554a53adf417bd611d04bbbb751%22%7D%7D'
        yield Request(ratebeer_url, callback=self.parse_ratebeer, meta={'beer': beer, 'item': item})

    def parse_ratebeer(self, response):
        beer = response.meta.get('beer')
        item = response.meta.get('item')

        data = json.loads(response.text)

        items = data.get('data', {}).get('results', {}).get('items', [])
        if items:
            score = items[0].get('beer', {}).get('overallScore')
            try:
                item['ratebeer_score'] = int(score)
            except:
                item['ratebeer_score'] = 'N/A'

        untappd_url = f'https://untappd.com/search?q={beer}'
        yield Request(untappd_url, callback=self.parse_untappd, meta={'beer': beer, 'item': item})

    def parse_untappd(self, response):
        beer = response.meta.get('beer')
        item = response.meta.get('item')

        first = response.css('div.beer-item>a::attr(href)').get()
        if first:
            yield Request(urljoin('https://untappd.com/', first), callback=self.parse_untappd_beer,
                          meta={'beer': beer, 'item': item})

    def parse_untappd_beer(self, response):
        beer = response.meta.get('beer')
        item = response.meta.get('item')

        soup = BeautifulSoup(response.text, 'html.parser')
        item['untappd_abv'] = soup.select_one('p.abv').text.strip()
        item['untappd_ibu'] = soup.select_one('p.ibu').text.strip()
        item['untappd_rating'] = soup.select_one('span.num').text.strip('(').strip(')')
        yield item
