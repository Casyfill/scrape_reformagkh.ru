# -*- coding: utf-8 -*-
import requests as rq
from lxml import html
import pandas as pd

from details import _parse_detailes
# import bs4

BASE_URL = 'https://www.reformagkh.ru'
# Хамовники
tid = 2281058

# def get_house_links():
# sort=name&order=asc&page=1&limit=100


def _get_last(dom):
    '''get number of pages for the query
    '''
    return int(dom.xpath("//ul[@class='pagination']/li[@class='last']/a/@data-page")[0])


def _parse_bld_row(bld):
    '''parse row and get result'''
    d = {
        'address': bld.xpath("./td[1]/a/text()")[0],
        'link': BASE_URL + bld.xpath("./td[1]/a/@href")[0],
        'price': bld.xpath("./td[2]/text()")[0].replace(' ', ''),
        'area': bld.xpath("./td[3]/text()")[0].replace(' ', ''),
        'management': bld.xpath("./td[4]/text()")[0]
    }

    if d['management'] == u'Не заполнено':
        d['management'] = None

    return d


def main(tid):
    '''get building data
    for the particular level of data
    '''
    url = BASE_URL + '/myhouse'
    # set session context
    s = rq.Session()
    params = {'tid': tid,
              'limit': 100,
              'order': 'asc',
              'page': 1}

    r = s.get(url, params=params)
    # print r.url
    dom = html.fromstring(r.text)
    last_page = _get_last(dom)

    bldngs = []
    for page in xrange(1, last_page + 1):
        params['page'] = page
        result = s.get(url, params=params)
        print result.url

        dom = html.fromstring(result.text)
        bldngs.extend(
            map(_parse_bld_row,
                dom.xpath("//div[@class='grid']/table/tbody/tr")))

    print 'Buildings scraped: {}'.format(len(bldngs))
    df = pd.DataFrame(bldngs)
    return df


def scrape_details(df):
    r = []
    for link in df['link'].tolist():
        if link is not None:
            r.append(_parse_detailes(link))

    details = pd.DataFrame(r)
    return df.merge(details, on='link', how='left')


if __name__ == '__main__':
    df = main(tid)

    df = scrape_details(df)
    print df.head(10)

    df.to_csv('Hamovniky.csv', encoding='utf8')
    
