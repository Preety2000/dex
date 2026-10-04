import os
import json
import datetime as dt
import xml.etree.ElementTree as ET

from includes.core.globals.entry import app_context
from includes.core.metadata import MetaData
from includes.database.models.secondary import Article, QuizQuestion, Terms
from includes.utils.arti import get_artical_url


class Sitemap:

    @staticmethod
    def sitemap():
        # Define the file path where we want to save the data
        file_path = os.path.join(app_context.folder.static_json, "sitemap.json")
        # Read the JSON file and convert it into a Python list
        with open(file_path, "r") as file:
            sitemap_url = json.load(file)

        # Get the last modification time of the file
        file_modification_timestamp = os.path.getmtime(file_path)

        # Convert the modification time to a datetime object in UTC
        modified_time = dt.datetime.utcfromtimestamp(file_modification_timestamp)

        # Format the datetime object to the desired format (including milliseconds)
        modification_date = (
            modified_time.strftime("%Y-%m-%dT%H:%M:%S.")
            + f"{modified_time.microsecond // 1000:03d}Z"
        )

        root = ET.Element("urlset")
        root.set("xmlns", "http://www.sitemaps.org/schemas/sitemap/0.9")
        for a in sitemap_url:
            item = ET.SubElement(root, "url")
            id_element = ET.SubElement(item, "loc")
            id_element.text = str(a)
            title_element = ET.SubElement(item, "lastmod")
            title_element.text = modification_date
            title_element = ET.SubElement(item, "changefreq")
            title_element.text = "monthly"
            author_element = ET.SubElement(item, "priority")
            author_element.text = str("1.0")

        # Convert to XML byte data
        xml_data = ET.tostring(root, encoding="utf-8", method="xml")
        return xml_data

    @staticmethod
    def opensearch():
        root = ET.Element("OpenSearchDescription")
        root.set("xmlns", "http://a9.com/-/spec/opensearch/1.1/")
        root.set("xmlns:moz", "http://www.mozilla.org/2006/browser/search/")

        ShortName = ET.SubElement(root, "ShortName")
        ShortName.text = MetaData.site_name

        Description = ET.SubElement(root, "Description")
        Description.text = MetaData.excerpt

        InputEncoding = ET.SubElement(root, "InputEncoding")
        InputEncoding.text = "UTF-8"

        Image = ET.SubElement(root, "Image ")
        Image.set("width", "16")
        Image.set("height", "16")
        Image.set("type", "image/x-icon")
        Image.text = app_context.request.host_url + "favicon.ico"

        Url = ET.SubElement(root, "Url")
        Url.set("method", "get")
        Url.set(
            "template",
            app_context.request.host_url
            + "search?q={searchTerms}&tag={searchTermsForTag}",
        )
        Url.set("type", "text/html")

        xml_data = ET.tostring(root)
        return xml_data

    @staticmethod
    def robots():
        # Open the text file and read its contents
        with open("robots.txt", "r") as file:
            file_content = file.read()

        # Send the content as plain text
        # return PlainTextResponse(content=file_content)
        return "xml_data"

    @staticmethod
    async def index():
        sitemap_url = []
        host_url = app_context.request.host_url
        sitemap_url.append(app_context.request.host_url[:-1])
        other = ["trending", "search", "courses", "topic", "exam"]

        category_all = app_context.db.query(Terms).all()
        sitemap_url.extend([host_url + item for item in other])

        # ARTICLE QUESTIONS
        tagged = [
            f"{host_url}questions/tagged/{category.slug}"
            for category in category_all
            if category.id != 0
        ]

        articals = []
        artical_all = app_context.db.query(Article).all()
        for artical in artical_all:
            if artical.status == "Publish":
                await get_artical_url(artical)
                articals.append(artical.url)

        #  MCQ / QUIZ QUESTIONS
        mcq_map = [f"{host_url}practice"]
        for category in category_all:
            url = f"{host_url}practice/tagged/{category.slug}"
            mcq_map.append(url)

        quiz_questions = app_context.db.query(QuizQuestion).all()
        mcq_questions = [
            f"{host_url}practice/{quiz_question.id}"
            for quiz_question in quiz_questions
            if quiz_question.status
        ]

        sitemap_url.extend(tagged)
        sitemap_url.extend(articals)
        sitemap_url.extend(mcq_questions)
        sitemap_url = sorted(sitemap_url)

        return sitemap_url
