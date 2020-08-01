# -*- coding: utf-8 -*-
import scrapy
from scrapy import Request


class AmazonLaptopReviewSpider(scrapy.Spider):
    name = 'amazon_laptop_review'
    allowed_domains = ['www.amazon.com']
    start_urls = ['https://www.amazon.com/s?k=laptop&i=amazon-devices&ref=nb_sb_noss_2']

    def parse(self, response):
        from scrapy.utils.response import open_in_browser
        open_in_browser(response)
        for links in response.css('div.sg-row div.a-section>h2.a-size-mini>a.a-link-normal'):
            product_link = links.css('::attr(href)').get()
            yield Request(response.urljoin(product_link), callback= self.parse_detail_page)

    def parse_detail_page(self, response):
        item = {}
        item['ProductName'] = response.css('span#productTitle::text').get().strip()
        item['ProductCode'] = response.css('table#productDetails_detailBullets_sections1 td.a-size-base::text').get().strip()
        item['ProductCodeType'] = response.css('table#productDetails_detailBullets_sections1 th.a-color-secondary::text').get().strip()
        item['AverageStar'] = response.css('i.a-icon>span.a-icon-alt::text').get().split(' ', 1)[0]
        item['Description'] = response.css('div#productDescription p::text').get()
        ReviewLink = 'https://www.amazon.com/product-reviews/{}'.format(item['ProductCode'])
        yield Request(ReviewLink, meta={'item':item}, callback=self.parse_review)

    def parse_review(self, response):
        item = response.meta.get('item')
        for review in response.css('div.review'):
            item['Reviewer'] = review.css('span.a-profile-name::text').get()
            item['Review'] = review.css('span.review-text-content>span::text').get()
            item['ReviewStar'] = review.css('span.a-icon-alt::text').get().split(' ',1)[0]
            item['ReviewDate'] = review.css('span.review-date::text').get()
            yield item
        next_page = response.css('ul.a-pagination li.a-last>a::attr(href)').get()
        if next_page:
            yield Request(response.urljoin(next_page), callback=self.parse_review())
