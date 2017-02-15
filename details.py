# -*- coding: utf-8 -*-
import requests as rq
from lxml import html
import time
# import pandas as pd
SLEEP = 8
ISSUES = []


def _process_pair(krow, vrow):
    '''get text for key and value elements'''
    k = krow.xpath("./td[1]/span/text()")[0]
    v = vrow.xpath("./td[2]/span/text()")[0]
    return k, v


def _process_table(table):
    '''process  table
    ignoring nested rows
    and return a dictionary '''
    keys = table.xpath("./tr[@class='left']")
    values = table.xpath("./tr[@class='left']/following-sibling::tr[1]")
    result = {
        k: v for k, v in [_process_pair(kr,
                                        vr) for kr, vr in zip(keys, values)]}
    return result


def _process_nested(row):
    '''process nested row
    and return table name
    and its values as a dict
    '''
    try:
        key = row.xpath("./td/span/text()")[0]
    except:
        key = '___'
    try:
        nested_table = row.xpath('./td/table/tbody')[0]
        result = _process_table(nested_table)
        r = {'_'.join([key, k]): v for k, v in result.iteritems()}
        return r
    except:
        return None


def flattern_dict(data_dict):
    '''flattern dictionary, one level deep'''
    d = {}
    for key in data_dict.keys():
        if isinstance(data_dict[key], dict):
            for inner_key in data_dict[key].keys():
                print 'key:', key
                new_key = '{0}_{1}'.format(key,
                                           inner_key)
                print 'new key:', new_key
                d[new_key] = data_dict[key][new_key]
        else:
            d[key] = data_dict[key]
    return d


def _parse_detailes(url):
    '''parse detailed building information from the url'''
    print url
    time.sleep(SLEEP)
    try:

        page = rq.get(url)
        page.encoding = 'utf-8'
        page.raise_for_status()
        dom = html.fromstring(page.text)

        table = dom.xpath(
            "//div[@class='numbered']/table[@class='col_list']/tbody")[0]
        # the table is formated so that each odd row has class='left'
        # and represent key,
        # and each even one - value, except cases where row is nested
        result = _process_table(table)
        result['link'] = url
        # one-level rows
        nested_rows = table.xpath("./tr[descendant::td[@colspan=2]]")
        for row in nested_rows:
            # print row.text_content()
            v = _process_nested(row)
            if v is not None:
                for key, value in v.iteritems():
                    result[key] = value

        return result

    except Exception as inst:
        print 'Error:',
        print(inst)
        ISSUES.append(url)
        return None
