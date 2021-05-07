import scrapy
import re
import dateparser

from tpdb.BaseSceneScraper import BaseSceneScraper


class SexMexSpider(BaseSceneScraper):
    name = 'SexMex'
    network = 'SexMex'
    parent = 'SexMex'
    site = 'SexMex'

    start_urls = [
        'https://sexmex.xxx/'
    ]

    selector_map = {
        'title': '',
        'description': '',
        'date': '',
        'image': '',
        'performers': '',
        'tags': "",
        'external_id': 'updates\/(.*)\.html$',
        'trailer': '',
        'pagination': '/tour/categories/movies_%s_d.html'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[@class="col-lg-4 col-md-4 col-xs-16 thumb"]')
        for scene in scenes:
            date = scene.xpath('./div/div/p[@class="scene-date"]/text()').get()
            date = dateparser.parse(date.strip()).isoformat()            
            title = scene.xpath('./div/div/h5/a/text()').get()
            if " . " in title:
                title = re.search('^(.*)\ \.\ ', title).group(1).strip()
            description = scene.xpath('./div/div/p[@class="scene-descr"]/text()').get()
            image = scene.xpath('./div/a/img/@src').get()
            if "transform.php" in image or "url=" in image:
                image = re.search('url=(.*)',image).group(1)
            performers = scene.xpath('./div/div/p[@class="cptn-model"]/a/text()').getall()
            
            sceneid = scene.xpath('./@data-setid').get()
            
            scene = scene.xpath('./div/a/@href').get()
            if sceneid:
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene,
                    meta={'date': date, 'title': title, 'description': description, 'image': image, 'performers': performers,'id': sceneid})

