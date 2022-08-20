import json

import scrapy
from scrapy import Request
import urllib.parse


class StatusSpider(scrapy.Spider):
    name = 'status'
    allowed_domains = ['salesweb.civilview.com']
    start_urls = ['https://salesweb.civilview.com/Sales/SalesSearch?countyId=28']
    custom_settings = {'ROBOTSTXT_OBEY': False, 'LOG_LEVEL': 'INFO',
                       'CONCURRENT_REQUESTS_PER_DOMAIN': 5,
                       'RETRY_TIMES': 5,
                       'FEED_URI': 'wesitedetail.csv',
                       'FEED_FORMAT': 'csv',
                       }

    def parse(self, response):
        dates = response.xpath("//select[@id='PropertyStatusDate']/option/text()").extract()
        for date in dates:
            if (date.startswith('07') or date.startswith('08') or date.startswith('09') or date.startswith(
                    '10') or date.startswith('11')) and date.endswith("2022"):
                url = 'https://salesweb.civilview.com/Sales/SalesSearch?countyId=28'
                body = 'PropertyTypeDesc=Real+Estate&RadioButtonValue=ALL&SheriffNumber=&PropertyStatusDate={}&MonthNumber=0&PlaintiffTitle=&DefendantTitle=&Address='.format(
                    urllib.parse.quote(date, safe=''))
                yield Request(url=url, body=body, method='POST', callback=self.parse_listing)

    def parse_listing(self, response):
        item = dict()
        tabel_row = response.xpath("//div[contains(@class,'table-responsive')]/table/tr")
        for td in tabel_row:
            item['case_no'] = td.xpath("./td[2]/text()").get()
            item['sales_date'] = td.xpath("./td[3]/text()").get()
            item['property_status'] = td.xpath("./td[4]/text()").get()
            item['case_title'] = td.xpath("./td[5]/text()").get()
            item['description'] = td.xpath("./td[6]/a/text()").get()
            picture_node = td.xpath("./td[7]/div/img/@src")
            if picture_node:
                item['picture'] = 'https://salesweb.civilview.com' + picture_node.get()
            else:
                item['picture'] = ''
            item['attorney'] = td.xpath("./td[8]/text()").get()
            item['writ_amount'] = td.xpath("./td[9]/text()").get()
            item['ter_and_con'] = td.xpath("./td[10]/text()").get()
            yield item
