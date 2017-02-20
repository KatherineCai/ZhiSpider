# -*-coding:utf-8-*-

import scrapy
from ZhiSpider.items import PaperItem

PAPER_URL = 'http://kns.cnki.net/KCMS/detail/detail.aspx?'
REF_URL = 'http://kns.cnki.net/kcms/detail/frame/list.aspx?'

_NAME_XPATH = '//*[@id="mainArea"]/div[2]/div[1]/h2/text()'
NAME_XPATH = '//*[@class="title"]/text()'
AUTHORS_XPATH = '//*[@class="author"]/span/a/@onclick'
INSTITUTIONS_XPATH = '//*[@class="orgn"]/span/a/@onclick'


class ReferenceSpider(scrapy.Spider):
    name = 'cnki.net'

    # allowed_domain = ['http://kns.cnki.net']

    def parse(self, response):

        def xpath(path):
            return self.xpath(path, response)

        def get_authors(path):
            authors = []
            for raw in xpath(path):
                # raw == 'TurnPageToKnet('au','Jack','123456')'
                splits = raw.split('\'')  # =['TurnPageToKnet(', 'au', ',', '梁德东', ',', '17491188', ');']
                #                         #   0                  1     2    3        4    5
                author = (splits[3], splits[5])
                authors.append(author)
            return authors

        def get_institutions(path):
            return get_authors(path)

        item = PaperItem()

        # get Paper's name & check if the page exsists
        name = xpath(NAME_XPATH)
        if len(name) == 0:
            return
        item['name'] = name[0]  # only 1 element

        # get 2nd part of page url
        url = response._url.split('?')[1]  # choose the part comes after '?'
        url = url.split('&v=')[0]  # cut the tail after '&v='
        item['href'] = url

        # get authors
        item['authors'] = get_authors(AUTHORS_XPATH)

        # get institutions
        item['institutions'] = get_institutions(INSTITUTIONS_XPATH)

        # get refs
        url = REF_URL + url + '&RefType=1'
        request = scrapy.Request(url, callback=self.parse_ref_page)
        request.meta['item'] = item
        return request

    def parse_ref_page(self, response):
        # todo
        pass

    @staticmethod
    def xpath(xpath, response, extract=True):
        assert isinstance(xpath, str)
        if extract:
            return response.selector.xpath(xpath).extract()
        else:
            return response.selector.xpath(xpath)

# sample url
#
#     http://kns.cnki.net/KCMS/detail/detail.aspx?dbcode=CMFD&dbname=CMFD0506&filename=2005109132.nh&
# http://kns.cnki.net/kcms/detail/frame/list.aspx?dbcode=CMFD&filename=2005109132.nh&dbname=CMFD0506&RefType=1&vl=
#     http://kns.cnki.net/KCMS/detail/detail.aspx?dbcode=CMFD&dbname=CMFD201402&filename=1014203205.nh&
#
# url pattern: ref.url = page.url + 'RefType=1'
