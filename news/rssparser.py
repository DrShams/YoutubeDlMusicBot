import os
import logging
import json
from urllib.parse import urlparse
import xml.etree.ElementTree as ET

import requests
from bs4 import BeautifulSoup


class RSSParser:
    """Class for parsing an RSS feed."""

    def __init__(self, rss_url):
        """Initialize the RSSParser."""
        self.url = rss_url
        self.latest_item = None
        self.latest_pub_date = None
        self.extracted_info = {}
        self.xml_content = None  # Move the definition here

    def fetch_rss_content(self):
        """Fetch the RSS content."""
        response = requests.get(self.url, timeout=60)
        self.xml_content = response.content
        logging.info("Content RSS was recieves")

    def parse_rss(self):
        """Parse the RSS content."""
        root = ET.fromstring(self.xml_content)

        #Retrieve only last element
        for item in root.findall(".//item"):
            pub_date = item.find("pubDate").text
            self.latest_item = item
            self.latest_pub_date = pub_date
            break
        logging.info("Last news was recieved")

    def clean_html_text(self, html_text):
        """Clean HTML text."""
        soup = BeautifulSoup(html_text, "html.parser")
        cleaned_text = ' '.join(soup.stripped_strings)
        return cleaned_text

    def extract_information(self):
        """Extract information from the latest news item."""
        if self.latest_item is not None:
            title = self.latest_item.find("title").text
            link = self.latest_item.find("link").text
            description_html = self.latest_item.find(".//description").text

            # Clean HTML tags and extra spaces
            description = self.clean_html_text(description_html)

            filename = self.retrieve_and_save_image(link)
            self.extracted_info = {
                "Title": title,
                "Description": description,
                #"Category": category,
                "Publication Date": self.latest_pub_date,
                "ImageFileName": filename  # Change this line
            }
            logging.debug(self.extracted_info)
            logging.info("Information was successefully extracted from HTML")
            return self.extracted_info
        else:
            logging.error("No matching news item found.")
            return None

    def retrieve_and_save_image(self, link):
        """Retrieve and save the image."""
        response = requests.get(link, timeout=60)
        html_content = response.content

        soup = BeautifulSoup(html_content, "html.parser")

        # Extract the image using the provided XPath
        image = soup.select_one("html > body > main > div:nth-of-type(3) > div > article > div > img")

        if image:
            image_url = image.get("src")
            self.extracted_info["Image URL"] = image_url

            # Download the image
            image_response = requests.get(image_url, timeout = 60)

            # Extract the file extension from the image URL
            parsed_url = urlparse(image_url)
            image_extension = os.path.splitext(os.path.basename(parsed_url.path))[1]

            # Save the image locally using the original file extension
            local_image_filename = f"image_temp{image_extension}"
            with open(local_image_filename, "wb") as image_file:
                image_file.write(image_response.content)

            logging.info(f"Image saved locally as {local_image_filename}")
            return local_image_filename
        else:
            logging.error("No image found on the page.")
            return None

    def save_to_json(self, filename="extracted_info.json"):
        """Save extracted information to JSON."""
        with open(filename, "w", encoding="utf-8") as json_file:
            json.dump(self.extracted_info, json_file, ensure_ascii=False, indent=2)
            logging.info(f"Extracted information saved to {filename}")
