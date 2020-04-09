from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from datetime import datetime
import requests
import json


class PriceProfit:
    def __init__(self):
        chromeOptions = webdriver.ChromeOptions()
        prefs = {"profile.managed_default_content_settings.images": 2}
        chromeOptions.add_experimental_option("prefs", prefs)
        self.driver = webdriver.Chrome(
            options=chromeOptions, executable_path=r"C:\\Users\\beroz\\Documents\\chromedriver.exe")

    def navigate_link(self, link):
        self.driver.get(link)

    def get_data(self):
        self.driver.get("https://evds2.tcmb.gov.tr/index.php?/evds/dashboard/4985")
        pre = self.driver.find_element_by_tag_name("pre").text
        data = json.loads(pre)
        print(data)


price_profit = PriceProfit()
price_profit.get_data()
