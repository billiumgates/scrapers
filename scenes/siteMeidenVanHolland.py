import scrapy
import re
import json
import codecs
import html
import dateparser
from tpdb.BaseSceneScraper import BaseSceneScraper

def match_tag(argument):
    match = {
        'debutanten': "First Time",
        'anaal': "Anal",
        'dikke tieten': "Big Boobs",
        'amateur sex': "Amateur",
        'volle vrouw': "BBW",
        'duo': "FM",
        'gangbang': "Gangbang",
        'trio': "Threesome",
        'jonge meid': "18+ Teens",
        'squirten': "Squirting",
        'pov': "POV",
        'lesbisch': "Lesbian",
        'pijpen': "Blowjob",
        'buitensex': "Outdoors",
        'bdsm': "BDSM",
        'rollenspel': "Roleplay",
        'internationaal': "International",
        'klassiekers': "Classics",
        'milf': "MILF",
    }
    return match.get(argument, '')

class siteMedienVanHolldandSpider(BaseSceneScraper):
    name = 'MeidenVanHolland'
    network = 'Meiden Van Holland'


    base_url = 'https://meidenvanholland.nl'
    
    headers_json = {
        'accept': 'application/json, text/plain, */*',
        'credentials': 'Syserauth 1-5d73b3eb1647d9e91a9d7280777c4aefe4d25efa1367f5bc5bd03121415038ac-6128070c',
        'origin': 'https://meidenvanholland.nl',
        'referer': 'https://meidenvanholland.nl',
    }

    selector_map = {
        'title': '//script[contains(text(),"NUXT")]/text()',
        're_title': 'video:\{title:\"(.*?)\"',
        'description': '//script[contains(text(),"NUXT")]/text()',
        're_description': 'description:\"(.*?)\"',
        'date': '//script[contains(text(),"NUXT")]/text()',
        're_date': 'pivot_data:\{active_from:\"(\d{4}-\d{2}-\d{2})',
        'image': '//meta[@name="og:image"]/@content',
        'performers': '//script[contains(text(),"NUXT")]/text()',
        're_performers': 'models:\[(.*?)\]',
        'tags': '//script[contains(text(),"NUXT")]/text()',
        'external_id': 'sexfilms\/(.*)',
        'trailer': '',
        'pagination': '/categories/movies_%s_d.html#'
    }
    
    def get_next_page_url(self, base, page):
        url = "https://api.sysero.nl/videos?page={}&count=20&include=images:types(thumb):limit(1|0),products,categories&filter[status]=published&filter[products]=1%2C2&filter[types]=video&sort[recommended_at]=DESC&frontend=1"
        return self.format_url(base, url.format(page))
        

    def start_requests(self):
        yield scrapy.Request(url=self.get_next_page_url(self.base_url, self.page),
                             callback=self.parse,
                             meta={'page': self.page},
                             headers=self.headers_json,
                             cookies=self.cookies)
    
    def parse(self, response, **kwargs):
        scenes = self.get_scenes(response)
        count = 0
        for scene in scenes:
            count += 1
            yield scene

        if count:
            if 'page' in response.meta and response.meta['page'] < self.limit_pages:
                meta = response.meta
                meta['page'] = meta['page'] + 1
                print('NEXT PAGE: ' + str(meta['page']))
                yield scrapy.Request(url=self.get_next_page_url(response.url, meta['page']),
                                     callback=self.parse,
                                     meta=meta,
                                     headers=self.headers_json,
                                     cookies=self.cookies)                             

    def get_scenes(self, response):
        global json
        jsondata = json.loads(response.text)
        data = jsondata['data']
        for jsonentry in data:
            if jsonentry['attributes']['slug']:
                scene_url = "https://meidenvanholland.nl/sexfilms/" + jsonentry['attributes']['slug']
                yield scrapy.Request(url=self.format_link(response, scene_url), callback=self.parse_scene)


    def get_performers(self, response):
        performers = self.process_xpath(response, self.get_selector_map('performers'))
        if performers:
            performers = performers.get()
            performers = re.search(',models:\[(.*id:\".*?)\],preroll', performers)
            if performers:
                performers = performers.group(1)
                performers = re.findall('title:\"(.*?)\"', performers)
                return list(map(lambda x: x.strip(), performers))

        return []
    


    def get_tags(self, response):
        tags = self.process_xpath(response, self.get_selector_map('tags'))
        if tags:
            tags = tags.get()
            tags = re.search(',categories:\[(.*?)\],products', tags)
            if tags:
                tags = tags.group(1)
                tags = re.findall('name:\"(.*?)\"', tags)
                tags2 = ['European']
                for tag in tags:
                    found_tag = match_tag(tag.lower())
                    if found_tag:
                        tags2.append(found_tag)
                return list(map(lambda x: x.strip().title(), tags2))

        return []
    

    def get_description(self, response):
        if 'description' not in self.get_selector_map():
            return ''

        description = self.process_xpath(response, self.get_selector_map('description'))
        if description:
            description = self.get_from_regex(description.get(), 're_description')

            if description:
                try:
                    description = codecs.decode(description, 'unicode-escape')
                except:
                    description = re.sub(r'\\u00\d[a-fA-F]','', description)
                description = re.sub('<[^<]+?>', '', description).strip()
                description = re.sub('[^a-zA-Z0-9\-_ \.\?\!]','', description)
                return html.unescape(description.strip())

        return ''
        

    def get_date(self, response):
        datestring = self.process_xpath(response, self.get_selector_map('date'))
        if datestring:
            datestring = datestring.get()
            date = self.get_from_regex(datestring, 're_date')
            if not date:
                date = re.search('active_from=\"(\d{4}-\d{2}-\d{2})',datestring)
                if date:
                    date = date.group(1)
                

            if date:
                return dateparser.parse(date).isoformat()
            else:
                return dateparser.parse('today').isoformat()

        return None
        
                

    def get_site(self, response):
        return "Meiden Van Holland"

    def get_parent(self, response):
        return "Meiden Van Holland"
        
