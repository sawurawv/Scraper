# -*- coding: utf-8 -*-
import re
from datetime import datetime

import scrapy
from scrapy import Request
from scrapy.utils.response import open_in_browser


class CampingfranceSpider(scrapy.Spider):
    name = 'campingfrance'
    allowed_domains = ['campingfrance.com']
    start_urls = ['https://www.campingfrance.com/uk/find-your-campsite']

    def parse(self, response):
        for links in response.css('article.bloc-art div.content-art>a'):
            link = links.css('::attr(href)').get()
            yield Request(response.urljoin(link), callback=self.parse_detail)

        next_page = response.css('div.lk-more-list>a::attr(href)').get()
        if next_page is not None:
            next_page = response.urljoin(next_page)
            yield Request(next_page, callback=self.parse)

    @staticmethod
    def parse_oc(date_txt):
        # for None type
        if not isinstance(date_txt, str):
            return '', ''

        if re.findall('from\s?(\d{2}/\d{2})\s?to\s?(\d{2}/\d{2})', date_txt.strip()):
            op, cl = re.findall('from\s?(\d{2}/\d{2})\s?to\s?(\d{2}/\d{2})', date_txt)[0]
            open_date = datetime.strptime(op, '%d/%m').strftime('%b %d')
            close_date = datetime.strptime(cl, '%d/%m').strftime('%b %d')
            return open_date, close_date
        else:
            return '', ''

    def parse_detail(self, response):
        item = {}
        item['Campsite'] = response.css('h1.camp-name::text').get().strip()
        item['Holiday Village'] = ''
        item['URL'] = response.url
        item['Telephone'] = response.css('a[href="#phone"]::attr(data-contact)').get().replace(' ','')
        item['Fax'] = ''
        item['Email'] = ''
        item['Website'] = response.css('div.bloc-one>a::attr(href)').get()

        dates = response.css('div.bloc-one>ul>li:nth-child(1) ::text').extract()
        if dates:
            item['Open Date'], item['Close Date'] = self.parse_oc(dates[-1])
        else:
            item['Open Date'], item['Close Date'] = '', ''

        item['Pitches'] = int(response.css('a[href="#mobilehome"]>strong::text').get() or 0)
        item['Bungalows'] = '' or 0
        item['Vans/Caravan/RV'] = '' or 0
        item['Apartment'] = '' or 0
        item['Total Spaces'] = item['Pitches'] + item['Bungalows'] + item['Vans/Caravan/RV'] + item['Apartment']
        item['Franchise/Group Name'] = ''
        item['Street Address'] = ''
        item['Zip Code'] = response.css('address.cf-city-dep span.txt strong::text').get().split(' ')[0]
        item['City'] = ''
        item['Region'] = response.css('address.cf-city-dep span.txt strong::text').get().split(' ')[1]
        item['Country'] = 'France'
        item['Latitude'] = ''
        item['Longitude'] = ''
        yield item