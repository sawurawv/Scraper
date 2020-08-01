import scrapy

class ethzSpider(scrapy.Spider):
    name = 'ethz'
    allowed_domains = ['ethz.ch']
    start_urls = ['https://www.ethz.ch/en/industry-and-society/entrepreneurship/pioneer-fellowships.html']

    def parse(self, response):
        for contents in response.css('div.scrollarea-content'):
            for content in contents.css('tr'):
                if content.css('td:nth-child(1)>a::text'):
                    item = {}
                    item['Pioneer_Fellow'] = content.css('td:nth-child(1)>a::text').extract_first().split('(')[0].strip()
                    item['ETH_Spin-off'] = content.css('td:nth-child(2)>a::text').extract_first()
                    item['Host_Professor'] = content.css('td:nth-child(3)::text').extract_first().split('(')[0].strip()
                    item['Dept'] = content.css('td:nth-child(3)::text').extract_first().split('(')[1].strip().strip(')')
                    item['Year'] = content.css('td:nth-child(1)>a::attr(href)').extract_first().split('/')[-2]
                    item['Pdf_link'] = response.urljoin(content.css('td:nth-child(1)>a::attr(href)').extract_first())
                    yield item