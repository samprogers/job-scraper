import requests
from django.conf import settings
from datascraper.models import Vendor, State
import dateutil, math, time, sys, json, dateparser
from concurrent.futures import ThreadPoolExecutor
from datascraper.services.http.httpthreading import HttpThreading
from datascraper.services.parser.stringextracter import StringExtracter
from datascraper.util.formattedjobposting import FormattedJobPosting
from bs4 import BeautifulSoup

class AdzunaApi:

    vendor = None
    thread_counter = 0
    api_key = settings.ADZUNA_API_KEY
    client_id = settings.ADZUNA_API_CLIENT_ID

    def __init__(self):
        self.vendor = Vendor.objects.get(slug='adzuna')
        self.states = State.objects.all()


    def getJobs(self, rsp):
        parser = StringExtracter()

        if rsp is None:
            return []

        jobs = []

        try:
            rsp = json.loads(rsp)
        except:
            return []

        results = rsp['results']
        for result in results:
            title = result['title']
            vendor_job_id = result['id']
            description = result['description']
            location = result['location']['area']
            url = result['redirect_url']
            published_at = result['created']
            company_name = result['company']['display_name'] if "display_name" in result['company'].keys() else ""
            state = parser.getState(json.dumps(location)) if location is not None else None
            is_usa = True
            is_remote = True if  parser.isRemote(json.dumps(location)) or parser.isRemote(title) else False

            if published_at is not None:
                published_at = dateparser.parse(published_at)
                published_at = published_at.strftime("%Y-%m-%d")

            formatted = FormattedJobPosting(
                url=url,
                title=title,
                description=description,
                vendor_job_id=vendor_job_id,
                company={"name": company_name, "slug": company_name.lower()},
                location=location,
                vendor=self.vendor,
                published_at=published_at,
                state=state,
                is_usa=is_usa,
                is_remote=is_remote,
            )
            jobs.append(formatted)

        return jobs

    def setDetails(self, url):
        self.thread_counter += 1
        print(self.thread_counter)
        if self.thread_counter % 3 == 0:
            time.sleep(10)

        rsp = requests.get(url)
        if rsp.status_code == 200:
            print(len(rsp.text))
            return rsp.json()
        else:
            print(rsp.status_code)
            return {'results': []}



    def getFormattedJobs(self, qry):

        pg = 1
        jobs = []
        all_urls = []
        api_responses = []
        api_threading = HttpThreading(3, 2, 30)
        detail_threading = HttpThreading(5, 5, 10)
        parser = StringExtracter()
        print(qry)

        first_url = f"https://api.adzuna.com/v1/api/jobs/us/search/{pg}?app_id={self.client_id}&app_key={self.api_key}&content-type=application/json&results_per_page=100&what={qry}&full_time=1&where=united+states"
        all_urls.append(first_url)
        print(first_url)

        rsp = requests.get(first_url).json()
        if "count" in rsp.keys():
            print(rsp["count"])
            pages = math.ceil(rsp["count"] / 100)

            for pg in range(1, pages):
                url = f"https://api.adzuna.com/v1/api/jobs/us/search/{pg}?app_id={self.client_id}&app_key={self.api_key}&content-type=application/json&results_per_page=100&what={qry}&full_time=1&where=united+states"
                all_urls.append(url)

        #get all url responses
        all_jobs = []

        #get responses and build all_jobs list
        print(all_urls)
        api_threading.executeGet(all_urls)
        responses = [api_threading.getLastResponse(url) for url in all_urls]
        [ all_jobs.extend(self.getJobs(r)) for r in responses]

        #get all detail urls
        detail_urls = [j.url for j in all_jobs]
        detail_threading.executeGet(detail_urls)

        for j in all_jobs:
            url = j.url
            print(url)
            j.description = detail_threading.getLastResponse(j.url)
            print(len(j.description))
            j.skills = parser.getSkills(j.description) if j.description is not None else []

        print("ALL JOBS!", len(all_jobs))
        return all_jobs