# -*- coding: utf-8 -*-
import json

import scrapy
from scrapy import Request


class KrogerSpider(scrapy.Spider):
    name = 'kroger'
    allowed_domains = ['www.kroger.com']
    start_urls = ['https://www.kroger.com/p/ritz-fresh-stacks-original-crackers/0004400003113',
                  'https://www.kroger.com/p/simple-truth-organic-tomato-ketchup/0001111085853',
                  'https://www.kroger.com/p/simple-truth-organic-spicy-black-beans/0001111087034',
                  'https://www.kroger.com/p/simple-truth-organic-garbanzo-beans/0001111084769',
                  'https://www.kroger.com/p/simple-truth-organic-black-beans/0001111084938',
                  'https://www.kroger.com/p/dickinson-s-sugar-free-blackberry-preserves/0005150003003',
                  'https://www.kroger.com/p/kroger-zesty-italian-dressing/0001111076241',
                  'https://www.kroger.com/p/kraft-miracle-whip-with-olive-oil/0002100004330',
                  'https://www.kroger.com/p/lala-pecan-cereal-yogurt-smoothies/0081547301546']

    def parse(self, response):
        item = {}
        item['Name'] = response.css('div.ProductDetails-header>h1::text').get()
        item['Quantity'] = response.css('span.ProductDetails-customerFacingSize>span::text').get()
        item['UPC'] = response.css('span.ProductDetails-upc>span::text').get().split(' ')[-1]
        item['Image'] = response.css('div.ImageLoader img::attr(data-src)').get()
        item['Product Detail'] = response.css('div.RomanceDescription>p::text').get('')
        yield Request(url=f'https://www.kroger.com/products/api/nutrition/details/{item["UPC"]}',
                      callback=self.parse_Nutrition, meta={'item': item})

    def parse_Nutrition(self, response):
        item = response.meta.get('item')
        json_data = json.loads(response.text)[0]
        item['Warning'] = json_data['allergens']
        item['Calories'] = json_data['nutritionFacts']['caloriesPerServing']
        n_item = {}
        for nut in json_data.get('nutritionFacts', {}).get('macronutrients', []):
            n_item[nut.get('title')] = f'{nut.get("amount")} {nut.get("unitOfMeasure")}'
            if nut.get('subNutrients'):
                for sub_nut in nut.get('subNutrients', []):
                    n_item[sub_nut.get('title')] = f'{sub_nut.get("amount")} {sub_nut.get("unitOfMeasure")}'
        for nut in json_data.get('nutritionFacts', {}).get('micronutrients', []):
            n_item[nut.get('title')] = f'{nut.get("dailyValue")} %'
            if nut.get('subNutrients'):
                for sub_nut in nut.get('subNutrients', []):
                    n_item[sub_nut.get('title')] = f'{sub_nut.get("dailyValue")} %'
        item['nutrients'] = n_item
        yield item