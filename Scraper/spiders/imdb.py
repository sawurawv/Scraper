# -*- coding: utf-8 -*-
import re

import scrapy
from scrapy import Request


class ImdbSpider(scrapy.Spider):
    name = 'imdb'
    allowed_domains = ['www.imdb.com']
    start_urls = ['https://www.imdb.com/feature/genre/?ref_=nv_ch_gr']

    def parse(self, response):

    	for movie_genres in response.css('div.ninja_image a'):
    		movie_genre = movie_genres.css('::attr(href)').get()
    		yield Request(response.urljoin(movie_genre), callback = self.parse_movies)


    def parse_movies(self, response):
    	
        for movies in response.css('div.lister-item'):
            item = {}
            item['Title'] = movies.css('h3.lister-item-header a::text').get()
            item['Link'] = response.urljoin(movies.css('h3.lister-item-header a::attr(href)').get())
            item['Run Time'] = movies.css('span.runtime::text').get()
            year = movies.css('span.lister-item-year::text').get()
            if year:
                item['Year'] = year.rsplit('(', 1)[-1].strip(')')
            item['Rating'] = movies.css('div.ratings-imdb-rating strong::text').get()
            item['Summary'] = ''.join(movies.css('p.text-muted::text').extract()).strip()
            names = ''.join(movies.xpath('.//p[contains(text(), "Director")]//text()').extract())
            item['Director'] = item['Stars'] = ''
            if names:
                directors = re.findall('Directors?\:(.*)?\|', names, re.DOTALL)
                if directors:
                    item['Director'] = ' '.join(directors[0].split())
                stars = re.findall('Stars?\:(.*)?$', names, re.DOTALL)
                if stars:
                    item['Stars'] = ' '.join(stars[0].split())
            item['Genre'] = movies.css('span.genre::text').get()
            item['Votes'] = movies.css('span[name="nv"]::attr(data-value)').get()
            yield item

        next_page = response.urljoin(response.css('a.next-page::attr(href)').get())
        if next_page:
            yield Request(next_page)
