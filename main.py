import scrapy
import json
from itemadapter import ItemAdapter
from scrapy.item import Item, Field
from scrapy.crawler import CrawlerProcess


class QuoteItem(Item):
    author = Field()
    quote = Field()
    tags = Field()


class AuthorItem(Item):
    full_name = Field()
    born_date = Field()
    born_location = Field()
    bio = Field()


class SpiderPipline(object):
    quotes = []
    authors = []

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        if "author" in adapter.keys():
            self.quotes.append(
                {
                    "author": adapter["author"],
                    "quote": adapter["quote"],
                    "tags": adapter["tags"],
                }
            )
        if "full_name" in adapter.keys():
            self.authors.append(
                {
                    "full_name": adapter["full_name"],
                    "born_date": adapter["born_date"],
                    "born_location": adapter["born_location"],
                    "bio": adapter["bio"],
                }
            )
        return item

    def close_spider(self, spider):
        with open("quotes.json", "w", encoding="utf-8") as fd:
            json.dump(self.quotes, fd, ensure_ascii=False)

        with open("authors.json", "w", encoding="utf-8") as fd:
            json.dump(self.authors, fd, ensure_ascii=False)


class Spider(scrapy.Spider):
    name = "my_spider"
    allowed_domains = ["quotes.toscrape.com"]
    start_urls = ["http://quotes.toscrape.com/"]
    custom_settings = {
        "ITEM_PIPELINES": {
            SpiderPipline: 300,
        }
    }

    def parse(self, response):
        for q in response.xpath('/html//div[@class="quote"]'):
            quote = q.xpath('span[@class="text"]/text()').get().strip()
            author = q.xpath('span/small[@class="author"]/text()').get().strip()
            tags = q.xpath('div[@class="tags"]/a[@class="tag"]/text()').extract()
            yield QuoteItem(author=author, quote=quote, tags=tags)
            
            path_author = q.css('.quote span a').attrib['href']
            yield response.follow(url=path_author, callback=self.parse_author)

        next_link = response.xpath("//li[@class='next']/a/@href").get()
        if next_link:
            yield response.follow(url=next_link, callback=self.parse)

    def parse_author(self, response):
        body = response.xpath('/html//div[@class="author-details"]')
        full_name = body.xpath('h3[@class="author-title"]/text()').get().strip()
        born_date = body.xpath('p/span[@class="author-born-date"]/text()').get().strip()
        born_location = (
            body.xpath('p/span[@class="author-born-location"]/text()').get().strip()
        )
        bio = body.xpath('div[@class="author-description"]/text()').get().strip()
        yield AuthorItem(
            full_name=full_name,
            born_date=born_date,
            born_location=born_location,
            bio=bio,
        )


if __name__ == "__main__":
    process = CrawlerProcess()
    process.crawl(Spider)
    process.start()
