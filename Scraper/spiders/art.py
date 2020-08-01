# -*- coding: utf-8 -*-
import re

import scrapy
from scrapy import Request


class ArtSpider(scrapy.Spider):
    name = 'art'
    allowed_domains = ['cdc.gov']

    def start_requests(self):
        states = ['AL', 'AK', 'AZ', 'AR', 'AA', 'AE', 'AP', 'CA', 'CO', 'CT', 'DE', 'DC', 'FL', 'GA', 'HI', 'ID', 'IL',
                  'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD', 'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ',
                  'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC', 'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA',
                  'WV', 'WI', 'WY']
        for state in states:
            yield scrapy.Request(
                'https://nccd.cdc.gov/drh_art/rdPage.aspx?rdReport=DRH_ART.ClinicsList&dtClinicslist-PageNr=1&'
                'rdDataCache=7164033889&rdShowModes=&rdSort=&rdNewPageNr=True1&rdAjaxCommand=RefreshElement&'
                'rdDataTablePaging=True&rdRefreshElementID=dtClinicslist&'
                'rdCSRFKey=d29a325e-1b03-49ee-9d68-e536068bf09e&rdShowElementHistory='
                f'&State={state}&Distance=1000', meta={'page': 1, 'state': state})

    def parse(self, response):
        for row in response.css('table#dtClinicslist>tr'):
            item = {'Clinic Name': "".join(row.css('td:nth-child(1) ::text').extract()),
                    'Street Address': row.css('td:nth-child(4)>span ::text').extract_first(),
                    'City': row.css('td:nth-child(3)>span ::text').extract_first(),
                    'State': row.css('td:nth-child(2)>span ::text').extract_first(),
                    'Zip': row.css('td:nth-child(5)>span ::text').extract_first(),
                    'Phone': row.css('td:nth-child(6)>span ::text').extract_first()}
            detail_url = response.urljoin(
                re.findall(r'javascript:NavigateLink2\(\'(.*?)\'', row.css('td:nth-child(1) a::attr(href)').get(''))[0])
            yield scrapy.Request(detail_url, callback=self.parse_name, meta={'item': item})
        next_button = response.css('span#dtClinicslist-NextPageCaption')
        if next_button:
            page = response.meta.get('page') + 1
            state = response.meta.get('state')
            yield scrapy.Request(
                f'https://nccd.cdc.gov/drh_art/rdPage.aspx?rdReport=DRH_ART.ClinicsList&dtClinicslist-PageNr={page}&'
                'rdDataCache=7164033889&rdShowModes=&rdSort=&rdNewPageNr=True1&rdAjaxCommand=RefreshElement&'
                'rdDataTablePaging=True&rdRefreshElementID=dtClinicslist&'
                'rdCSRFKey=d29a325e-1b03-49ee-9d68-e536068bf09e&rdShowElementHistory='
                f'&State={state}&Distance=1000', meta={'page': 1, 'state': state})
        yield Request

    def parse_name(self, response):
        for info in response.xpath('//span[text()="Medical Director"]/../../following-sibling::span'):
            item = {}
            item['Medical Director First Name'] = info.xpath('/text()').extract_first().split(',')[0].split(' ')[0]
            item['Medical Director Last Name'] = response.xpath('/text()').extract_first().split(',')[0].split(' ')[2]
            yield item