import xml.etree.ElementTree as ET
import requests
from bs4 import BeautifulSoup
import json

class RSSParser:
    def __init__(self, rss_url):
        self.url = rss_url
        self.latest_item = None
        self.latest_pub_date = None
        self.extracted_info = {}

    def fetch_rss_content(self):
        response = requests.get(self.url)
        self.xml_content = response.content

    def parse_rss(self):
        root = ET.fromstring(self.xml_content)

        for item in root.findall(".//item"):
            pub_date = item.find("pubDate").text
            # if pub_date == last_build_date:
            self.latest_item = item
            self.latest_pub_date = pub_date
            break

    def clean_html_text(self, html_text):
        soup = BeautifulSoup(html_text, "html.parser")
        cleaned_text = ' '.join(soup.stripped_strings)
        return cleaned_text

    def extract_information(self):
        if self.latest_item is not None:
            title = self.latest_item.find("title").text
            link = self.latest_item.find("link").text
            description_html = self.latest_item.find(".//description").text

            # Clean HTML tags and extra spaces
            description = self.clean_html_text(description_html)

            category = self.latest_item.find("category").text
            guid = self.latest_item.find("guid").text

            # Save extracted information to a dictionary
            self.extracted_info = {
                "Title": title,
                "Description": description,
                "Category": category,
                "Publication Date": self.latest_pub_date,
                "Link": link
            }

            # Retrieve and save the image URL
            self.retrieve_and_save_image(link)

        else:
            print("No matching news item found.")

    def retrieve_and_save_image(self, link):
        response = requests.get(link)
        html_content = response.content

        # Use BeautifulSoup to parse the HTML content
        soup = BeautifulSoup(html_content, "html.parser")

        # Extract the image using the provided XPath
        image = soup.select_one("html > body > main > div:nth-of-type(3) > div > article > div > img")

        if image:
            image_url = image.get("src")
            self.extracted_info["Image URL"] = image_url
        else:
            print("No image found on the page.")

    def save_to_json(self, filename="extracted_info.json"):
        with open(filename, "w", encoding="utf-8") as json_file:
            json.dump(self.extracted_info, json_file, ensure_ascii=False, indent=2)
            print(f"Extracted information saved to {filename}")

    def post_to_vk_wall(self, token, owner_id, from_group, version_vk):
        url = "https://api.vk.com/method/wall.post"
        message = json.dumps(self.extracted_info, ensure_ascii=False, indent=2)

        photo = "photo151028064_457244654"
        print(photo)
        response = requests.post(
            url=url,
            params={
                'access_token': token,
                'from_group': from_group,
                'owner_id': owner_id,
                'message': message,
                'attachments': photo,
                'v': version_vk
            }
        )

        print(response.json())        

if __name__ == "__main__":
    rss_parser = RSSParser("https://www.votpusk.ru/news.xml")
    rss_parser.fetch_rss_content()
    rss_parser.parse_rss()
    rss_parser.extract_information()
    rss_parser.save_to_json()

    # You need to replace these with your actual VK API credentials

    vk_token="vk1.a.QG6IKCYi17wbV1JtEq_NHHhCyMXz_enHlBOMqgpfCHKd7WhACXk_Bhr7XVqD_6Txjf_Zf4AwsJE0cA-K8K2rwk0KXc6A5r-klyeFITGPQE-bnSunUnmWVtiGRwMbXLk9uv8FouyRCjzb6Kbyn_qph4oK3hEhyujb3Lrn0ExL_55hY_MeQZh5Ntrwwx5qnC6W3tTgcF_dCfdarqgF91i2sw"
    access_token="vk1.a.iz-qPCHE3i5yCps4oXNmmllM0cL8VVkAtgRiD1LgtcyLtMjoQgdAy-EHgrnyxwur0BNwfAMGTWAsUMUsdGKTyB7cBX30fEpQmwXXvdion31JnOG8AQTqinFVhzFc8H8T0XqOEOMYJJwyP66YFxqmBkxj9YzqZfTZ3lM5FoogtjpBlhzLarM8WA0348A6ynPfAtllPFZxN0-4l-6gRsYSvg"
    vk_owner_id = -50679937
    vk_from_group = 1
    vk_version = "5.133"

    rss_parser.post_to_vk_wall(access_token, vk_owner_id, vk_from_group, vk_version)