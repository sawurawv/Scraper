# -*- coding: utf-8 -*-
import scrapy
from scrapy import Request


class BedrijvenSpider(scrapy.Spider):
    name = 'bedrijven'
    allowed_domains = ['bedrijven.xyz']
    start_urls = ['https://bedrijven.xyz']

    def parse(self, response):
        for links in response.css('ul.home-category-list>li>a'):
            link = links.css('::attr(href)').get()
            yield Request(response.urljoin(link), callback=self.parse_company_list)

    def parse_company_list(self,response):
        for links in response.css('div.company-list div.item>a'):
            link = links.css('::attr(href)').get()
            yield Request(response.urljoin(link), callback=self.parse_detail)

        next_page = response.xpath('//ul[@class="pagination"]/li[contains(., "»")]/a/@href').get()
        if next_page:
            yield Request(response.urljoin(next_page))


    def parse_detail(self,response):
        item = {}
        item['Name'] = response.xpath('//td[text()="Handelsnaam:"]/following-sibling::td/text()').get()
        item['Description'] = response.css('div[itemprop="description"]>p::text').get()
        item['Category'] = response.xpath('//td[text()="Categorie:"]/following-sibling::td/text()').get()
        item['Legal form']= response.xpath('//td[text()="Rechtsvorm:"]/following-sibling::td/text()').get()
        item['Branch number']= response.xpath('//td[text()="Vestigingsnummer:"]/following-sibling::td/text()').get()
        item['Chamber of Commerce number'] = response.xpath('//td[text()="KVK nummer:"]/following-sibling::td/text()').get()
        item['Phone number'] = response.xpath('//td[text()="Telefoonnummer:"]/following-sibling::td/text()').get()
        item['Website'] = response.xpath('//td[text()="Website:"]/following-sibling::td/text()').get()
        item['Street'] = response.xpath('//td[text()="Straat:"]/following-sibling::td/text()').get()
        item['Postcode'] = response.xpath('//td[text()="Postcode:"]/following-sibling::td/text()').get()
        item['Place'] = response.xpath('//td[text()="Plaats:"]/following-sibling::td/text()').get()
        item['Province'] = response.xpath('//td[text()="Provincie:"]/following-sibling::td/text()').get()
        item['URL'] = response.url
        yield item