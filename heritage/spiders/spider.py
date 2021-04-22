import re
import scrapy
from scrapy.loader import ItemLoader
from ..items import HheritageItem
from itemloaders.processors import TakeFirst

pattern = r'(\xa0)?'


class HheritageSpider(scrapy.Spider):
    name = 'heritage'
    start_urls = ['https://www.heritage.com.au/about/news']

    def parse(self, response):
        post_links = response.xpath('//li[@class="list-group-item actual-group-item"]/a/@href').getall()
        yield from response.follow_all(post_links, self.parse_post)

    def parse_post(self, response):
        date = response.xpath('//div[@class="h-container  "]/p/text()').get()
        if date:
            date_check = re.match(r'\d+\s\w+\s\d+',date)
            if not date_check:
                date = 'Not stated in article'
        else:
            try:
                date = response.xpath('//meta[@name="description"]/@content').get().split('Published')[1]
            except:
                date = 'Not stated in article'
        title = response.xpath('//h1/text()').get()
        content = response.xpath('//div[@class="h-container  "]//text()').getall()
        if re.search(r'\d+\s\w+\s\d+',' '.join(content)):
            content = content[2:]
        content = [p.strip() for p in content if p.strip()]
        content = re.sub(pattern, "", ' '.join(content))

        item = ItemLoader(item=HheritageItem(), response=response)
        item.default_output_processor = TakeFirst()

        item.add_value('title', title)
        item.add_value('link', response.url)
        item.add_value('content', content)
        item.add_value('date', date)

        yield item.load_item()
