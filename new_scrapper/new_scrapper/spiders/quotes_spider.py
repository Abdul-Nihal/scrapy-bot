import  pandas as pd
import json,re

from datetime import datetime
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver



import scrapy
class QuotesSpider(scrapy.Spider):
    name = "quotes"

    allowed_domains = ["rewardsforjustice.net"]
    start_urls = ["https://rewardsforjustice.net/index/?jsf=jet-engine:rewards-grid&tax=crime-category:1070%2C1071%2C1073%2C1072%2C1074"]
    doc = []
    print("Started Scrapy")


    def parse(self, response):
        try:
            page_no = 1
            links = True
            rewards = []
            while links:
                driver = webdriver.Chrome(executable_path=ChromeDriverManager().install())
                driver.get(
                    "https://rewardsforjustice.net/index/?jsf=jet-engine:rewards-grid&tax=crime-category:1070%2C1071%2C1073%2C1072%2C1074&pagenum={}".format(
                        str(
                            page_no)))

                links = driver.find_elements(By.CLASS_NAME, "jet-engine-listing-overlay-wrap")


                for i in links:
                    rewards.append(i.get_attribute('data-url'))
                driver.quit()
                page_no = page_no + 1
                print(page_no)
                # links =False
        except Exception as e:
            print("err:",str(e))

        try:
            for link in rewards:
                # Follow each link and extract the required parameters
                yield scrapy.Request(link, callback=self.parse_link)
        except Exception as e:
            print(str(e))

    #
    def parse_link(self,response):
        try:

            dic = {}
            dic["Page URL"] = self.get_url(response)
            dic ["Category"] = self.get_category(response)
            dic["Title"] = self.get_title(response)
            dic["Reward Amount"] = self.get_reward(response)
            dic["Associated Organization(s)"] = self.get_asso_org(response)
            dic["Associated Location(s)"] = self.get_asso_loc(response)
            dic["About"] = self.get_about(response)
            dic["Image URL"] = self.get_image_url(response)
            dic["Date Of Birth"] = self.get_dob(response)
            self.doc.append(dic)

            # print(dic["dob"])
            print(len(self.doc))


        except Exception as e:
            print(str(e))
            # pass

    def get_category(self,response):
        try:
            class_name = response.xpath('//div[@data-elementor-type="single-post"]/@class').get()
            match = re.search(r'crime-category-(.*?)\slocation-country', class_name)
            if match:
                extracted_text = match.group(1)
                # print(extracted_text)
            else:
                return None
            return extracted_text
        except:
            return None

    def get_about(self,response):
        try:
            para_list = response.xpath("//div[@class='elementor-element elementor-element-52b1d20 elementor-widget elementor-widget-theme-post-content']//div[@class='elementor-widget-container']/p/text()").getall()
            about = ''.join(para_list)
            return about
        except:
            return None

    def get_dob(self,response):
        try:
            dob = response.xpath(
                "//div[@class='elementor-element elementor-element-9a896ea dc-has-condition dc-condition-empty elementor-widget elementor-widget-text-editor']//div[@class='elementor-widget-container']/text()").get()
            dob = dob.strip() if dob else None
            return dob
        except:
            return None
    def get_image_url(self,response):
        try:
            image_url = response.xpath('//a[@data-elementor-open-lightbox="yes"]/@href').get()
            return image_url
        except:
            return None

    def get_title(self,response):
        try:
            for sel in response.xpath(
                    '//div[@class="elementor-element elementor-element-f2eae65 elementor-widget elementor-widget-heading"]'):
                title = sel.xpath('.//h2/text()').get().strip()
                # print("title:",title)
            return title
        except:
            return None
    def get_url (self,response):
        try:
            return response.url
        except:
            return None

    def get_reward(self,response):
        try:
            for sel in response.xpath('//div[@class="elementor-element elementor-element-5e60756 dc-has-condition dc-condition-less elementor-widget elementor-widget-heading"]'):
                reward = sel.xpath('.//h2/text()').get().strip()
                # print("\treward:",reward)
            return reward
        except:
            return  None

    def get_asso_org(self,response):
        try:
            associate_org = response.xpath("//div[@class='elementor-element elementor-element-b7c9ae6 dc-has-condition dc-condition-empty elementor-widget elementor-widget-text-editor']//div[@class='elementor-widget-container']/text()").get()
            associate_org = associate_org.strip() if associate_org else None
            return associate_org
        except:
            return None

    def get_asso_loc(self, response):
        try:
            # associate_loc =response.xpath("//div[@class='elementor-element elementor-element-0fa6be9 dc-has-condition dc-condition-empty elementor-widget elementor-widget-jet-listing-dynamic-terms']//div[@class='nested-div-classname']//div[@class='nested-div-classname']/text()").get()
            associate_loc = response.xpath("//div[@class='elementor-element elementor-element-0fa6be9 dc-has-condition dc-condition-empty elementor-widget elementor-widget-jet-listing-dynamic-terms']//div[@class='jet-listing jet-listing-dynamic-terms']//span[@class='jet-listing-dynamic-terms__link']/text()").get()
            associate_loc = associate_loc.strip() if associate_loc else None
            return associate_loc
        except:
            return None

    def closed(self, reason):
        try:
            now = datetime.now()
            current_time = now.strftime("%Y%m%d_%H%M%S")
            json_file_name = f"{self.name}_{current_time}.json"
            xlxs_file_name = f"{self.name}_{current_time}.xlsx"
            # Write the data to a new JSON file
            with open(json_file_name, 'w') as f:
                data = {"data":self.doc}
                json.dump(data, f, indent=4)
            df = pd.DataFrame(self.doc)
            df.to_excel(xlxs_file_name, index=False)
            print("Saved and Closed ")

        except Exception as e:
            print(str(e))







