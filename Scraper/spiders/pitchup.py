# -*- coding: utf-8 -*-
import scrapy
from scrapy import Request


class PitchupSpider(scrapy.Spider):
    name = 'pitchup'
    allowed_domains = ['pitchup.com']
    start_urls = ['https://www.pitchup.com/en-us/search/usa/']

    def parse(self, response):
        for links in response.xpath(
                '//div[contains(@class, "searchResult")]//h4[contains(@class, campsite-name-title)]/a'):
            link = links.xpath('./@href').get()
            yield Request(response.urljoin(link), callback=self.parse_detail)

        next_page = response.xpath('//div[contains(@class, "paging")]//a[contains(text(), "Next")]/@href').get()
        if next_page is not None:
            next_page = response.urljoin(next_page)
            yield Request(next_page, callback=self.parse)

    def parse_detail(self, response):

        item = {}
        item['Campsite'] = response.css('div.campsite-header h1::text').get()
        item['Holiday Village'] = ''
        item['URL'] = response.url
        item['Telephone'] = ''
        item['Fax'] = ''
        item['Email'] = ''
        item['Website'] = ''
        item['Close Date'] = response.xpath('//div[@class="side_box dates"]/p/@data-opening-date').get()
        item['Open Date'] = response.xpath('//div[@class="side_box dates"]/p/@data-closing-date').get()

        item['Pitches'] = int(''.join(response.xpath('//div[@title="Tent sites"]/parent::div[@class="holder"]/text()').extract()).strip()or 0)
        item['Bungalows'] = int(''.join(response.xpath('//div[@title="Lodges, cabins, pods or huts"]/parent::div[@class="holder"]/text()').extract()).strip() or 0)
        item['Vans/Caravan/RV'] = int(''.join(response.xpath('//div[@title="RV sites"]/parent::div[@class="holder"]/text()').extract()).strip() or 0)
        item['Apartment'] = 0
        item['Total Spaces'] = item['Pitches']+item['Bungalows']+item['Vans/Caravan/RV']+item['Apartment']
        item['Franchise/Group Name'] = ''
        item['Street Address'] = response.css('ul>li.adr::text').get('').split(',')[0].strip()
        item['Zip Code'] = response.css('ul>li.adr::text').get().split(',')[-1].strip()
        item['City'] = response.css('ul>li.adr::text').get().split(',')[1].strip()
        item['Region'] = response.css('ul>li.adr::text').get().split(',')[2].strip()
        item['Country'] = response.css('ul>li.adr::text').get().split(',')[3].strip()
        item['Latitude'] =  response.css('div.campsite-location-info ul li:nth-child(2) span::text').extract()[0]
        item['Longitude'] = response.css('div.campsite-location-info ul li:nth-child(2) span::text').extract()[1]
        yield item
