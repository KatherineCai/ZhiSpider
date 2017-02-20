# -*-coding:utf-8-*-

import scrapy
import ZhiSpider

PAPER_URL = 'http://kns.cnki.net/KCMS/detail/detail.aspx?'
REF_URL = 'http://kns.cnki.net/kcms/detail/frame/list.aspx?'
NAME_XPATH =    '//*[@id="mainArea"]/div[2]/div[1]/h2/text()'
# AUTHORS_XPATH = '//*[@id="mainArea"]/div[4]/div[1]/div[1]'
AUTHORS_XPATH = '//*[@class="author"]/span/a/@onclick'
INSTITUTIONS_XPATH = '//*[@class="orgn"]/span/a/@onclick'

class ReferenceSpider(scrapy.Spider):
    name = 'http://kns.cnki.net/'
    allowed_domain = ['cnki.net']

    def parse(self, response):

        def xpath(Xpath, extract=True):
            assert isinstance(Xpath, str)
            if extract:
                return response.selector.xpath(Xpath).extract()
            else:
                return response.selector.xpath(Xpath)

        def get_authors(Xpath):
            authors = []
            for raw in xpath(Xpath):
                # raw == 'TurnPageToKnet('au','Jack','123456')'
                splits = raw.split('\'')  # =['TurnPageToKnet(', 'au', ',', '梁德东', ',', '17491188', ');']
                #                        #   0                  1     2    3        4    5
                author = (splits[3], splits[5])
                authors.append(author)
            return authors

        def get_institutions(Xpath):
            return get_authors(Xpath)

        # get Paper's name
        item = ZhiSpider.Paper()
        item['name'] = xpath(NAME_XPATH)[0] # only 1 element

        # get 2nd part of page url
        item['href'] = response._url.split('?')[1] # choose the part comes after '?'

        # get authors
        item['authors'] = get_authors(AUTHORS_XPATH)

        # get institutions
        item['institutions'] = get_institutions(INSTITUTIONS_XPATH)

# sample url
#
#     http://kns.cnki.net/KCMS/detail/detail.aspx?dbcode=CMFD&dbname=CMFD0506&filename=2005109132.nh&
# http://kns.cnki.net/kcms/detail/frame/list.aspx?dbcode=CMFD&filename=2005109132.nh&dbname=CMFD0506&RefType=1&vl=
#     http://kns.cnki.net/KCMS/detail/detail.aspx?dbcode=CMFD&dbname=CMFD201402&filename=1014203205.nh&
#
# url pattern: ref.url = page.url + 'RefType=1'
