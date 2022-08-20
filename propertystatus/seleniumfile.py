import csv
import json
import os
import time

from scrapy.http import HtmlResponse
import undetected_chromedriver.v2 as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re


def csv_writer(property_detail_list):
    headers = ['case_no', 'sales_date', 'property_status', 'case_title', 'description', 'picture', 'attorney',
               'writ_amount', 'ter_and_con', 'Tax Bill Number', 'Municipal District', 'Location Address',
               'Property Class', 'Special Tax District', 'Subdivision Name', 'Zoning District', 'Land Area (sq ft)',
               'Building Area (sq ft)', 'Revised Bldg Area (sq ft)', 'Square', 'Book', 'Lot/Folio', 'Line',
               'Legal Description', 'Assessment Area', 'Parcel Map', 'owner']
    try:
        with open('output.csv', 'w', newline='', encoding='UTF-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=headers)
            writer.writeheader()
            writer.writerows(property_detail_list)
    except IOError:
        print("I/O error")


def get_property_detail():
    property_detail_list = []
    for detail_row in csv.DictReader(open('wesitedetail.csv', encoding='utf-8')):
        try:
            address = detail_row['description']
            search_address = re.split("New", address, flags=re.IGNORECASE)[0]
            if search_address:
                property_info = {}
                driver = uc.Chrome(version_main=103)
                wait = WebDriverWait(driver, 20)
                url = 'https://beacon.schneidercorp.com/Application.aspx?AppID=979&LayerID=19792&PageTypeID=2&PageID=8661'
                driver.get(url)
                ter_and_con = wait.until(EC.presence_of_element_located(
                    (By.XPATH, "//div[@class='modal-footer']/a[contains(text(),'Agree')]")))
                ter_and_con.click()
                search_element = wait.until(
                    EC.presence_of_element_located((By.ID, 'ctlBodyPane_ctl01_ctl01_txtAddress')))
                search_element.send_keys(search_address)
                driver.find_element(By.ID, 'ctlBodyPane_ctl01_ctl01_btnSearch').click()

                property_info['case_no'] = detail_row['case_no']
                property_info['sales_date'] = detail_row['sales_date']
                property_info['property_status'] = detail_row['property_status']
                property_info['case_title'] = detail_row['case_title']
                property_info['description'] = detail_row['description']
                property_info['picture'] = detail_row['picture']
                property_info['attorney'] = detail_row['attorney']
                property_info['writ_amount'] = detail_row['writ_amount']
                property_info['ter_and_con'] = detail_row['ter_and_con']
                response = HtmlResponse(url=url, body=driver.page_source, encoding='utf-8')
                no_result = response.xpath("//div[@id='ctlBodyPane_noDataList_pnlNoResults']/label/text()")
                if no_result:
                    print(no_result.get())
                    property_detail_list.append(property_info)
                    driver.quit()
                else:
                    summery_nodes = response.xpath(
                        "//section[@id='ctlBodyPane_ctl00_mSection']/div/div/table[contains(@class,'tabular-data-two-column')]/tbody/tr")
                    for summery_node in summery_nodes:
                        col_name = summery_node.xpath("./th/strong/text()").get()
                        col_value = summery_node.xpath("./td/span/text()").get()

                        if col_name is None:
                            col_name = summery_node.xpath("./th/br/following-sibling::text()").get().strip()
                        if col_value is None:
                            col_value = summery_node.xpath("./td/a/@href").get()

                        property_info[col_name.replace("\n", '').strip()] = col_value
                    property_info['owner'] = ','.join(
                        response.xpath("//div[@class='four-column-blocks']/span/text()").extract())

                    property_detail_list.append(property_info)
                    driver.quit()
        except:
            continue
    csv_writer(property_detail_list)


if __name__ == '__main__':
    get_property_detail()
