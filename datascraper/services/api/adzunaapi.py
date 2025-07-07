import requests
from datascraper.models import Vendor, State
import dateutil, math, time, sys, json
from concurrent.futures import ThreadPoolExecutor
from datascraper.services.http.httpthreading import HttpThreading
from datascraper.services.parser.countryparser import CountryParser
from bs4 import BeautifulSoup

class AdzunaApi:

    vendor = None
    thread_counter = 0

    def __init__(self):
        self.vendor = Vendor.objects.get(slug='adzuna')
        self.states = State.objects.all()


    def getJobs(self, rsp):
        parser = CountryParser()

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

            formatted = {
                "url": url,
                "title": title,
                "company": {"name": company_name, "slug": company_name.lower() },
                "vendor": self.vendor,
                "location": location,
                "vendor_job_id": vendor_job_id,
                "published_at": dateutil.parser.parse(published_at),
                'description': description,
                "state": state,
                'is_usa': is_usa,
                'is_remote': is_remote
            }
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
        threading = HttpThreading(3, 2, 30)


        first_url = f"https://api.adzuna.com/v1/api/jobs/us/search/{pg}?app_id=e52c7895&app_key=488c4bc623d5271dd8af90c1ba682e7f&content-type=application/json&results_per_page=100&what={qry}&full_time=1&where=united+states"
        all_urls.append(first_url)

        rsp = requests.get(first_url).json()
        if "count" in rsp.keys():
            print(rsp["count"])
            pages = math.ceil(rsp["count"] / 100)

            for pg in range(1, pages):
                url = f"https://api.adzuna.com/v1/api/jobs/us/search/{pg}?app_id=e52c7895&app_key=488c4bc623d5271dd8af90c1ba682e7f&content-type=application/json&results_per_page=100&what={qry}&full_time=1&where=united+states"
                all_urls.append(url)

        print(all_urls)
        #get all url responses
        all_jobs = []

        #get responses and build all_jobs list
        threading.executeGet(all_urls)
        responses = [threading.getLastResponse(url) for url in all_urls]
        [ all_jobs.extend(self.getJobs(r)) for r in responses]

        print("ALL JOBS!", len(all_jobs))
        return all_jobs