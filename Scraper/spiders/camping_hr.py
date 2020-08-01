# -*- coding: utf-8 -*-
import scrapy
from scrapy import Request
from scrapy.utils.response import open_in_browser


class CampingHrSpider(scrapy.Spider):
    name = 'camping_hr'
    allowed_domains = ['camping.hr']
    start_urls = ['https://www.camping.hr/croatian-campsites']
    def parse(self, response):
        for links in response.xpath('//li[contains(@class, "serp__item")]//h2/a'):
            link = links.xpath('./@href').get()
            yield Request(response.urljoin(link), callback=self.parse_detail)

        next_page = response.css('a.next-link::attr(href)').get()
        if next_page is not None:
            next_page = response.urljoin(next_page)
            yield Request(next_page, callback=self.parse)

    def parse_detail(self, response):
        item = {}
        item['Campsite'] = response.xpath('//h1[contains(@class, "camp__main-title")]//text()').extract()[2].strip()
        item['Holiday Village'] = ''
        item['URL'] = response.url
        item['Telephone'] = response.xpath('//strong[text()="Telephone:"]/following-sibling::a/@href').get()
        item['Fax'] = response.xpath('//strong[text()="Fax:"]/following-sibling::a/@href').get()
        item['Email'] = response.css('a[data-fbq="KampEmail"]::attr(title)').get('').strip()
        item['Website'] = response.xpath('//strong[text()="Web:"]/following-sibling::a/@href').get()
        item['Close Date'] = ''
        item['Open Date'] = ''
        item['Pitches'] = int(response.css('li.sadrzaj_ostalo_ukupno_broj_parcela span strong::text').get('0').strip())
        item['Bungalows'] = int(response.css('p.sadrzaj_ostalo_najam_mobilnih_kucica span strong::text').get('0').strip())
        item['Vans/Caravan/RV'] = int(response.css('p.sadrzaj_ostalo_mogucnost_najma_kamp_prikolica span strong::text').get('0'))
        item['Apartment'] = 0
        item['Total Spaces'] = item['Pitches']+item['Bungalows']+item['Vans/Caravan/RV']+item['Apartment']
        item['Franchise/Group Name'] = ''
        item['Street Address'] = ''
        item['Zip Code'] = response.css('ul#site-contact-details li:nth-child(2)::text').extract()[1].split()[0].split('-')[1]
        item['City'] = response.css('ul#site-contact-details li:nth-child(2)::text').extract()[1].split()[1].split(',')[0]
        item['Region'] = response.css('ul#site-contact-details a#hlLink::text').get()
        item['Country'] = 'Croatia'
        item['Latitude'] = response.css('p.gps-widget__text::text').extract()[1].strip()
        item['Longitude'] = response.css('p.gps-widget__text::text').extract()[3].strip()
        yield item
