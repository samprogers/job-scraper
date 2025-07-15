from bs4 import BeautifulSoup
import re, sys, html

class HTMLParser(BeautifulSoup):

    def __init__(self):
        self.soup = None

    def getCompanyName(self, content):

        self.soup = BeautifulSoup(content, "html.parser")
        company_span = self.soup.find("span", {"class": "company-name"})

        if company_span is not None:
            raw_text = company_span.get_text()
            company = raw_text.replace("at ", "")
            company = re.sub("\s+", " ", company).strip().lower().replace(" ", "")
            return company

    def cleanHTMLString(self, text):
        self.soup = BeautifulSoup(html.unescape(text), "html.parser")
        for script in self.soup(["script", "style", 'a','title','head']):
            script.decompose()

        elements = [x.get_text() if x.get_text() != "" else " " for x in self.soup.find_all() if x.get_text() != ""]
        return '\n'.join(elements)

