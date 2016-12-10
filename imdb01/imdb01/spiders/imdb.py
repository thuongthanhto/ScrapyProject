# -*- coding: utf-8 -*-
import scrapy
from scrapy import Spider
from scrapy.conf import settings
from scrapy.selector import Selector
from scrapy.http.request import Request
from imdb01.items import Imdb01Item

class ImdbSpider(scrapy.Spider):
	name = "imdb"
	allowed_domains = ["imdb.com"]
	start_urls = settings['START_URLS']
	# data protocol
	protocol = "http"
	base_url = "www.imdb.com"

	def parse(self, response):
		sel = Selector(response)
		url_list = sel.xpath('//tbody[@class="lister-list"]/tr/td[@class="titleColumn"]/a/@href').extract()
		movies_urls = []
		for url in url_list:
			movies_urls.append(self.protocol + "://" + self.base_url + url)
		for movies_url in movies_urls:
			yield Request(movies_url, callback=self.parse_movies)     

	def parse_movies(self, response): 
		sel = Selector(response)
		item = Imdb01Item()
		item['movie_id'] = response.request.url.split('/')[4]
		item['img_src'] = self.get_img_src(sel)
		item['name'] = self.get_movie_name(sel)
		item['produced'] = self.get_production_year(sel)
		item['duration'] = self.get_duration(sel)
		item['genre'] = self.get_genre(sel)
		item['released'] = self.get_release_date(sel)
		item['rating'] = self.get_rating(sel)
		item['rating_cnt'] = self.get_rating_count(sel)
		item['description'] = self.get_description(sel)
		item['director'] = self.get_director(sel)
		item['writer'] = self.get_writer(sel)
		item['cast'] = self.get_cast(sel)
		return item
		
	def trim(self, raw_str):
		return raw_str.encode('ascii', errors='ignore').strip()
	
	def trim_list(self, raw_list):
		return [self.trim(raw_str) for raw_str in raw_list]
		
	def get_img_src(self, selector):
		try:
			img_src = selector.xpath('//div[@class="poster"]/a/img/@src').extract()[0]
			return self.trim(img_src)
		except IndexError:
			img_src = ''
			return img_src

	def get_movie_name(self, selector):
		try:
			movie_name = selector.xpath('//h1[@itemprop ="name"]/text()').extract()[0]
			return self.trim(movie_name)
		except IndexError:
			movie_name = ''
			return movie_name

	def get_production_year(self, selector):
		try:
			production_year = selector.xpath('//span[@id="titleYear"]/a/text()').extract()[0]
			return self.trim(production_year)
		except IndexError:
			production_year = ''
			return production_year
	
	def get_duration(self, selector):
		try:
			duration = selector.xpath('//div[@class="txt-block"]/time[@itemprop="duration"]/text()').extract()[0]
			return int(self.trim(duration).split()[0])
		except IndexError:
			duration = ''
			return duration

	def get_genre(self, selector):
		try:
			genre = selector.xpath('//span[@itemprop="genre"]/text()').extract()
			return self.trim_list(genre)
		except IndexError:
			genre = ''
			return genre

	def get_release_date(self, selector):
		try:
			release_date = selector.xpath('//meta[@itemprop="datePublished"]/@content').extract()[0]
			return self.trim(release_date)
		except IndexError:
			release_date = ''
			return release_date	
		
	def get_rating(self, selector):
		try:
			rating = selector.xpath('//span[@itemprop="ratingValue"]/text()').extract()[0]
			return float(self.trim(rating))
		except IndexError:
			rating = ''
			return rating
				
	def get_rating_count(self, selector):
		try:
			rating_count = selector.xpath('//span[@itemprop="ratingCount"]/text()').extract()[0]
			return int(self.trim(rating_count).replace(',', ''))
		except IndexError:
			rating_count = 0
			return rating_count
		
	def get_description(self, selector):
		try:
			description = selector.xpath('//div[@itemprop="description"]/p/text()').extract()[0]
			return self.trim(description)
		except IndexError:
			description = ''
			return description
		
	def get_director(self, selector):
		try:
			director = selector.xpath('//span[@itemprop="director"]/a/span[@itemprop="name"]/text()').extract()
			return self.trim_list(director)
		except IndexError:
			director = ''
			return director
		
	def get_writer(self, selector):
		try:
			writer = selector.xpath('//span[@itemprop="creator"]/a/span[@itemprop="name"]/text()').extract()
			return self.trim_list(writer)
		except IndexError:
			writer = ''
			return writer
	
	def get_cast(self, selector):
		try:
			cast = selector.xpath('//span[@itemprop="actors"]/a/span/text()').extract()
			return filter(None, self.trim_list(cast))
		except IndexError:
			cast = ''
			return cast
		
