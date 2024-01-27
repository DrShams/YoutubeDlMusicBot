import xml.etree.ElementTree as ET
import requests
from bs4 import BeautifulSoup
import json
import os
from urllib.parse import urlparse
import logging

class RSSParser:
    def __init__(self, rss_url):
        self.url = rss_url
        self.latest_item = None
        self.latest_pub_date = None
        self.extracted_info = {}

    def fetch_rss_content(self):
        response = requests.get(self.url)
        self.xml_content = response.content
        logging.info("Content RSS was recieves")

    def parse_rss(self):
        root = ET.fromstring(self.xml_content)

        #Retrieve only last element
        for item in root.findall(".//item"):
            pub_date = item.find("pubDate").text
            # if pub_date == last_build_date:
            self.latest_item = item
            self.latest_pub_date = pub_date
            break
        logging.info("Last news was recieved")

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

            #category = self.latest_item.find("category").text
            guid = self.latest_item.find("guid").text

            # Save extracted information to a dictionary
            filename = self.retrieve_and_save_image(link)
            self.extracted_info = {
                "Title": title,
                "Description": description,
                #"Category": category,
                "Publication Date": self.latest_pub_date,
                "ImageFileName": filename  # Change this line
            }
            #logging.info(self.extracted_info)
            logging.info("Information was successefully extracted from HTML")
            return filename
        else:
            logging.info("No matching news item found.")

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

            # Download the image
            image_response = requests.get(image_url)
            
            # Extract the file extension from the image URL
            parsed_url = urlparse(image_url)
            image_filename, image_extension = os.path.splitext(os.path.basename(parsed_url.path))

            # Save the image locally using the original file extension
            local_image_filename = f"image_temp{image_extension}"
            with open(local_image_filename, "wb") as image_file:
                image_file.write(image_response.content)

            logging.info(f"Image saved locally as {local_image_filename}")
            return local_image_filename
        else:
            logging.error("No image found on the page.")

    def save_to_json(self, filename="extracted_info.json"):
        with open(filename, "w", encoding="utf-8") as json_file:
            json.dump(self.extracted_info, json_file, ensure_ascii=False, indent=2)
            logging.info(f"Extracted information saved to {filename}")