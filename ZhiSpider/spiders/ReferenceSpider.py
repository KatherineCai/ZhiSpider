# -*-coding:utf-8-*-

import scrapy
from ZhiSpider.items import PaperItem

PAPER_URL = 'http://kns.cnki.net/KCMS/detail/detail.aspx?'
REF_URL = 'http://kns.cnki.net/kcms/detail/frame/list.aspx?'


# NAME_XPATH = '//*[@class="title"]/text()'
# AUTHORS_XPATH = '//*[@class="author"]/span/a/@onclick'
# INSTITUTIONS_XPATH = '//*[@class="orgn"]/span/a/@onclick'

# TARGET_TITLE = '中国学术期刊网络出版总库'
# TARGET_XPATH = '//*[@class="dbTitle"]/text()'



class ReferenceSpider(scrapy.Spider):
    name = 'cnki.net'

    # allowed_domain = ['http://kns.cnki.net']
    start_urls = [
        'http://kns.cnki.net/KCMS/detail/detail.aspx?dbcode=CMFD&dbname=CMFD2010&filename=2009202861.nh'
    ]

    def parse(self, response):

        NAME_XPATH = '//*[@class="title"]/text()'
        AUTHORS_XPATH = '//*[@class="author"]/span/a/@onclick'
        INSTITUTIONS_XPATH = '//*[@class="orgn"]/span/a/@onclick'

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
        url = self.get_url(response)
        item['href'] = url

        # get authors
        item['authors'] = get_authors(AUTHORS_XPATH)

        # get institutions
        item['institutions'] = get_institutions(INSTITUTIONS_XPATH)

        # get refs
        item['refs'] = []
        url = REF_URL + url + '&RefType=1'
        request = scrapy.Request(url, callback=self.parse_ref_page)
        request.meta['item'] = item
        request.meta['is_first'] = True
        yield request

    def parse_ref_page(self, response):

        TARGET_TITLE = '中国学术期刊网络出版总库'
        NEXT_STR = '下一页'
        BOXES_XPATH = '//*[@class="essayBox"]'
        TARGET_XPATH = './/*[@class="dbTitle"]/text()'
        LIST_XPATH = './/li'
        PAGE_BAR_XPATH = './/*[@class="pageBar"]'
        REF_COUNT_XPATH = '//*[@id="pc_CJFQ"]/text()'

        item = response.meta['item']

        # check if the page's empty
        sels = response.selector.xpath(BOXES_XPATH)
        if not sels:
            yield item
            return

        # choose target part
        for sel in sels:  # sel is <essayBox>
            tmp = sel.xpath(TARGET_XPATH).extract()
            if sel.xpath(TARGET_XPATH).extract()[0] == TARGET_TITLE:
                break
        else:  # if fail, return
            yield item

        # get url & name
        refs = []
        for tags_li in sel.xpath(LIST_XPATH):  # tags_li is <li>
            name_pos = 1
            raw_list = tags_li.xpath('*')  # raw_list is a selector
            url = ''
            name = ''
            if raw_list[name_pos].xpath('@href'):
                url = raw_list[name_pos].xpath('@href').extract()[0]
                name = raw_list[name_pos].xpath('text()').extract()[0]
            else:
                name = tags_li.xpath('text()').extract()
            refs.append((name, url))
        item['refs'].extend(refs)

        # raise other pages
        if not response.meta['is_first']:
            temp1 = response.meta['ref_count']
            temp2 = len(item['refs'])
            if response.meta['ref_count'] == len(item['refs']):
                yield item
            return
        ref_count = int(response.selector.xpath(REF_COUNT_XPATH).extract()[0])
        page_count = (ref_count - 1) // 10 + 1
        while page_count > 1:
            url = self.get_url(response)
            url = REF_URL + url + '&CurDBCode=CJFQ&page=' + str(page_count)
            request = scrapy.Request(url, callback=self.parse_ref_page)
            request.meta['item'] = item
            request.meta['is_first'] = False
            request.meta['ref_count'] = ref_count
            yield request
            page_count -= 1

        # # check for next page
        # tags_a = sel.xpath(PAGE_BAR_XPATH)
        # tmp = response.selector.extract()
        # if tags_a:  # check page bar
        #     tmp = tags_a.extract()
        #     for tag in tags_a:
        #         tmp = tag.xpath('text()')
        #         if tag.xpath('text()').extract()[0] == NEXT_STR:  # check next page button
        #             url = tag.xpath('@href').extract()
        #             request = scrapy.Request(url, callback=self.parse_ref_page)
        #             request.meta['item'] = item
        #             return request
        # return item

    @staticmethod
    def xpath(xpath, response, extract=True):
        assert isinstance(xpath, str)
        if extract:
            return response.selector.xpath(xpath).extract()
        else:
            return response.selector.xpath(xpath)

    @staticmethod
    def get_url(response):
        url = response._url.split('?')[1]  # choose the part comes after '?'
        url = url.split('&v=')[0]  # cut the tail after '&v='
        return url

# sample url
#
#     http://kns.cnki.net/KCMS/detail/detail.aspx?dbcode=CMFD&dbname=CMFD0506&filename=2005109132.nh&
# http://kns.cnki.net/kcms/detail/frame/list.aspx?dbcode=CMFD&filename=2005109132.nh&dbname=CMFD0506&RefType=1&vl=
#     http://kns.cnki.net/KCMS/detail/detail.aspx?dbcode=CMFD&dbname=CMFD201402&filename=1014203205.nh&
#
# url pattern: ref.url = page.url + 'RefType=1'
