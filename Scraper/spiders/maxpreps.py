# -*- coding: utf-8 -*-
import json

import scrapy
from scrapy import Request


class MaxprepsSpider(scrapy.Spider):

    name = 'maxpreps'
    allowed_domains = ['www.maxpreps.com']
    start_urls = ['https://www.maxpreps.com/search/default.aspx?type=school&search=&state=tx&gendersport=boys,football']
    states = {
        'AK': 'Alaska',
        'AL': 'Alabama',
        'AR': 'Arkansas',
        'AS': 'American Samoa',
        'AZ': 'Arizona',
        'CA': 'California',
        'CO': 'Colorado',
        'CT': 'Connecticut',
        'DC': 'District of Columbia',
        'DE': 'Delaware',
        'FL': 'Florida',
        'GA': 'Georgia',
        'GU': 'Guam',
        'HI': 'Hawaii',
        'IA': 'Iowa',
        'ID': 'Idaho',
        'IL': 'Illinois',
        'IN': 'Indiana',
        'KS': 'Kansas',
        'KY': 'Kentucky',
        'LA': 'Louisiana',
        'MA': 'Massachusetts',
        'MD': 'Maryland',
        'ME': 'Maine',
        'MI': 'Michigan',
        'MN': 'Minnesota',
        'MO': 'Missouri',
        'MP': 'Northern Mariana Islands',
        'MS': 'Mississippi',
        'MT': 'Montana',
        'NA': 'National',
        'NC': 'North Carolina',
        'ND': 'North Dakota',
        'NE': 'Nebraska',
        'NH': 'New Hampshire',
        'NJ': 'New Jersey',
        'NM': 'New Mexico',
        'NV': 'Nevada',
        'NY': 'New York',
        'OH': 'Ohio',
        'OK': 'Oklahoma',
        'OR': 'Oregon',
        'PA': 'Pennsylvania',
        'PR': 'Puerto Rico',
        'RI': 'Rhode Island',
        'SC': 'South Carolina',
        'SD': 'South Dakota',
        'TN': 'Tennessee',
        'TX': 'Texas',
        'UT': 'Utah',
        'VA': 'Virginia',
        'VI': 'Virgin Islands',
        'VT': 'Vermont',
        'WA': 'Washington',
        'WI': 'Wisconsin',
        'WV': 'West Virginia',
        'WY': 'Wyoming'
    }

    def parse(self, response):
        for links in response.css('ul.team-levels>li[data-js-hook="link-varsity"]>a'):
            link = links.css('::attr(href)').get()
            yield Request(response.urljoin(link), callback=self.parse_roster)

    def parse_roster(self, response):

        roster_link = response.css('dl>dd>a[data-la="roster"]::attr(href)').get()
        yield Request(response.urljoin(roster_link), callback=self.parse_list_of_players)

    def parse_list_of_players(self, response):
        for players in response.css('table#roster>tbody>tr'):
            item = {}
            player = players.css('th>a::attr(href)').get()
            item['jersey'] = players.css('td.jersey::text').get('')
            position = list(map(str.strip, players.css('td.position::text').get('').split(',')))
            if position:
                item['primary_position'] = position[0]
                if len(position)>1:
                    item['secondary_position'] = position[1]
            item['weight'] = players.css('td.weight::text').get()
            item['height'] = json.loads(players.css('td.height::attr(data-json)').get()).get('value', 0)
            yield Request(response.urljoin(player), callback=self.parse_detail, meta={'item': item})

    def parse_detail(self, response):
        item = response.meta['item']
        item['first_name'] = response.css('h1.athlete-name>a span::text').extract()[0]
        item['last_name'] = response.css('h1.athlete-name>a span::text').extract()[1]
        item['player_url'] = response.url
        item['full_name'] = item['first_name'] + ' ' + item['last_name']
        item['graduation_year'] = response.css('span.graduation-year::text').get('').split(' ')[-1]
        item['high_school'] = response.css('div.row>a>span.school-name::text').get()
        item['city'] = response.css('div.row>a>span.school-city::text').get()
        item['state_abbr'] = response.css('div.row>a>span.school-state::text').get()
        item['state_name'] = self.states.get(item['state_abbr'])
        try:
            item['main_photo'] = response.urljoin(response.css('a.img::attr(style)').get().split('"')[1])
        except:
            item['main_photo'] = 'https://maxpreps.cbsistatic.com/includes/images/site_themes/no-photo-male.png'
        yield item