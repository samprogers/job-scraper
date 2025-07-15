import sys

from django.conf import settings
from serpapi import GoogleSearch
import requests, urllib, dateparser
from datascraper.services.parser.htmlparser import HTMLParser
from datascraper.models import Vendor
from datascraper.services.parser.stringextracter import StringExtracter
from datascraper.util.formattedjobposting import FormattedJobPosting

class CompanyGoogleSearch:

    api_key = settings.SEARCH_API_KEY
    search = None
    vendor = None

    def __init__(self):
        self.vendor = Vendor.objects.get(slug='google')

    def getCompanyResults(self, query='site:boards.greenhouse.io "ai"',num_results=100,start=0):
        self.search = GoogleSearch(
            {
                "q": query,
                "engine": "google",
                "api_key": self.api_key,
                "num": num_results,  # Max results per page is 20
                "start": start,
                "location": "United+States"
            }
        )
        return self.search.pagination()

    def getJobResults(self, query='site:boards.greenhouse.io "ai"',next_page_token=None):
        params =    {
            "q": query,
            #'uule': 'w+CAIQICINVW5pdGVkIFN0YXRlcw',
            'hl': 'en',  # language of the search
            'gl': 'us',
            "engine": "google_jobs",
            "api_key": self.api_key,
            "num": 10,  # Max results per page is 20
            #"start": start,
            "location": "Massachusetts+United+States"
        }
        url = f"https://serpapi.com/search.json?engine=google_jobs&gl=us&google_domain=google.com&hl=en&location={params['location']}&q={params['q']}&num={params['num']}&api_key={params['api_key']}"

        if next_page_token is not None:
            url = url + f"&next_page_token={next_page_token}"

        return requests.get(url).json()

    def getJobs(self, queries):
        jobs = []
        parser = StringExtracter()

        for query in queries:
            print(query)

            next_page_token = None
            while True:
                results = self.getJobResults(query=query, next_page_token=next_page_token)
                if 'serpapi_pagination' in results.keys():
                    next_page_token = results['serpapi_pagination']['next_page_token']
                else:
                    break

                for job in results.get("jobs_results", []):
                    vendor_job_id = job["job_id"]
                    title = job["title"]
                    job_company = job["company_name"] if job["company_name"] is not None else None
                    content = job["description"]
                    location = job["location"] if "location" in job.keys() else None
                    url = job["share_link"]
                    published_at = job["detected_extensions"]['posted_at'] if "detected_extension" in job.keys() and "posted_at" in job["detected_extensions"].keys() else None
                    is_usa = parser.isLocationInUSA(location) if location is not None else True
                    state = parser.getState(location) if location is not None else None
                    is_remote = True if parser.isRemote(location) or parser.isRemote(title) else False
                    skills = parser.getSkills(content) if content is not None else ""

                    if published_at is not None:
                        published_at = dateparser.parse(published_at)
                        published_at = published_at.strftime("%Y-%m-%d")

                    formatted = FormattedJobPosting(
                        url=url,
                        title=title,
                        description=content,
                        vendor_job_id=vendor_job_id,
                        company={"name": job_company, "slug": job_company},
                        location=location,
                        vendor=self.vendor,
                        published_at=published_at,
                        state=state,
                        is_usa=is_usa,
                        is_remote=is_remote,
                        skills=skills
                    )

                    if is_usa:
                        jobs.append(formatted)
                        print(len(jobs))

        return jobs

    def getCompanies(
            self,
            page_size=100,
            start=0,
            query='site:boards.greenhouse.io "ai"',
            current_list=[],
    ):
        companies = []
        pages = self.getCompanyResults(query=query, num_results=page_size, start=start)
        #print(self.search.get_dict())
        for page in pages:
            print(f"Current page: {page['serpapi_pagination']['current']}")
            for res in page.get("organic_results", []):
                link = res.get("link")
                parsed = urllib.parse.urlparse(link)

                if parsed is None:
                    continue

                print(link)
                path = parsed.path
                split_path = path.split("/")
                split_path = list(filter(lambda x: x != "", split_path))

                if len(split_path) == 0:
                    continue

                formatted_link = parsed.scheme + "://" + parsed.netloc + parsed.path
                if "myworkdayjobs.com" in formatted_link or "myworkday.com" in formatted_link:
                    parsed_qry = urllib.parse.parse_qs(parsed.query)
                    url_split = parsed.netloc.split(".")

                    if 'drs' in split_path:

                        if 's' not in parsed_qry:
                            continue
                        else:
                            tennant = parsed_qry['s'][0]
                            company = parsed_qry['t'][0]
                            url_split = parsed.netloc.split(".")
                            formatted_link = f"https://{tennant}.{url_split[0]}.myworkdayjobs.com/{company}"
                    elif 'job' in split_path:
                        _, _, string_end = link.partition("job/")
                        formatted_link = link.replace(f"job/{string_end}", "")
                        company = url_split[0]
                    else:
                        company = url_split[0]

                    formatted = {
                        'api_link': formatted_link,
                        'name': company,
                        'slug': company,
                    }
                    companies.append(formatted)
                    current_list.append(company)

                elif formatted_link and "boards.greenhouse.io" in formatted_link:
                    company = split_path[0]
                    formatted = {
                        'api_link': formatted_link,
                        'name': company,
                        'slug': company.lower(),
                    }
                    companies.append(formatted)
                    current_list.append(company)

                elif split_path[0] == "embed":
                    parser = HTMLParser()
                    rsp = requests.get(link)
                    company = parser.getCompanyName(rsp.content)
                    if company is not None:
                        companies.append(company)
                        current_list.append(company)

        return companies
