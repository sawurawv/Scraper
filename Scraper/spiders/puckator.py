# -*- coding: utf-8 -*-
import scrapy
import html2text
from datetime import date
from scrapy import FormRequest, Request
from scrapy.exceptions import CloseSpider


class PuckatorSpider(scrapy.Spider):
    name = 'puckator'
    allowed_domains = ['puckator.co.uk']
    start_urls = ['https://www.puckator.co.uk/customer/account/']

    password = 'H0spital1'
    email = 'devon@bktrade.org'

    def is_logged_in(self, response):
        return self.email in ''.join(response.css('div.box-information div.box-content ::text').extract())

    def parse(self, response):
        form_key = response.css('input[name="form_key"]::attr(value)').get()
        login_url = response.css('form.form-login::attr(action)').get()
        yield FormRequest(login_url, formdata={'form_key': form_key, 'login[username]': self.email,
                                               'login[password]': self.password, 'send': ''}, callback=self.after_login)

    def after_login(self, response):
        if not self.is_logged_in(response):
            raise CloseSpider(f'Can not login using credentials: email = {self.email}, password = {self.password}')

        for menues in response.css('li.parent>a'):
            drop_down_menu = menues.css('::attr(href)').get()
            if not drop_down_menu.endswith(('new-top-sellers.html', 'sale.html')):
                yield Request(drop_down_menu, callback=self.parse_item_links)

    def parse_item(self, response):
        for items in response.css('li.item>a'):
            item = items.css('::attr(href)').get()
            yield Request(item, callback=self.parse_product_listing)

    def parse_product_listing(self, response):
        for link in response.css('a.product-item-link'):
            product_link = link.css('::attr(href)').get()
            yield Request(product_link, callback=self.parse_detail)

    def parse_detail(self, response):
        item = {}
        item['Name'] = response.css('span[itemprop="name"]::text').get()
        item['Product Code'] = response.css('div.share-and-short::text').get().split('-')[-1].strip()
        item['CrawledDate'] = date.today()
        item['ProductURL'] = response.url
        if response.css('div.product-info-price span.old-price'):
            item['Old price'] = response.css(
                'div.product-info-price span.old-price span.price-wrapper::data-price-amount').get()
            item['Special price'] = response.css(
                'div.product-info-price span.special-price span.price-wrapper::data-price-amount').get()
        else:
            item['Price'] = response.css('div.product-info-price span.price-wrapper::data-price-amount').get()
        item['Description'] = html2text.html2text(response.css('div.description').get())
        item['Image url'] = response.css('figure.mz-figure>img::attr(src)').get()

        yield item