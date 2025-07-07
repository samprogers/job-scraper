from bs4 import BeautifulSoup
import re,sys

class CompanyHTMLParser(BeautifulSoup):

    def getCompanyName(self, content):
        soup = BeautifulSoup(content, "html.parser")
        company_span = soup.find("span", {"class": "company-name"})

        if company_span is not None:
            raw_text = company_span.get_text()
            company = raw_text.replace("at ", "")
            company = re.sub("\s+", " ", company).strip().lower().replace(" ", "")
            return company
