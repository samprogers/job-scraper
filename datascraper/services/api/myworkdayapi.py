import requests
from datascraper.models import Vendor
import dateutil, json, dateparser, math, urllib, time, sys
from bs4 import BeautifulSoup
from datascraper.services.http.httpthreading import HttpThreading
from datascraper.services.parser.countryparser import CountryParser
from functools import reduce


class MyWorkdayApi:

    vendor = None

    def __init__(self):
        self.vendor = Vendor.objects.get(slug='myworkday')

    def formatJob(self, company, parsed, tenant, job) -> dict:

        parser = CountryParser()
        if "title" not in job.keys():
            return None

        title = job["title"]
        path = job['externalPath']

        url = f"{parsed.scheme}://{parsed.netloc}/{tenant}{path}"
        content = ""

        vendor_job_id = job['bulletFields'][0] if 'bulletFields' in job.keys() else None
        published_at = job['postedOn'].replace('Posted', '').replace('+',
                                                                     '').strip() if "postedOn" in job.keys() else None
        location = job['locationsText'] if "locationsText" in job.keys() else None
        is_remote = True if parser.isRemote(location) or parser.isRemote(title) else False
        is_usa = parser.isLocationInUSA(location) if location is not None else False
        state = parser.getState(location)

        if published_at is not None:
            published_at = dateparser.parse(published_at)
            print(published_at)

        print(f"{company.name} - {title} - {location}")
        return {
            "url": url,
            "title": title,
            "description": content,
            "company": {"name": company.name, "slug": company.slug, "api_link": company.api_link},
            "vendor": self.vendor,
            "location": location,
            "vendor_job_id": vendor_job_id,
            "published_at": published_at,
            "is_usa": is_usa,
            "is_remote": is_remote,
            "is_hybrid": parser.isRemote(location),
            "state": state
        }


    def getJobResponse(self, url, offset=0, locationKey="Location_Country", locationVal="bc33aa3152ec42d4995f4791a106ed09"):
        print(offset)
        print(url)

        payload = {
            "appliedFacets": {
                #"locationCountry": ["bc33aa3152ec42d4995f4791a106ed09"],
                locationKey: [locationVal],
            },
            "limit": 20,
            "offset": offset,
            "searchText": ""
        }
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Accept-Language': 'en-US'
        }

        if locationKey is None:
            del payload["appliedFacets"]

        r = requests.post(url, data=json.dumps(payload), headers=headers)
        return r.json()


    def getNextPage(self, url, offset):
        return self.getJobResponse(url, offset=offset)


    def findLocation(self, job_url, slug, tenant, netloc):

        locationVals = ["e57e6863118d01e99264027e342bb6ba","bc33aa3152ec42d4995f4791a106ed09", "41fb57c284ed015efdf4553adb0e95a8","bc33aa3152ec42d4995f4791a106ed09", "c66d738416b74fb180376cf59cc7ec8f", "6669335a15de0119e2e6f81a6100246a","77feeca0d2d101d752185678b076fe24"]
        url = f"https://{netloc}/wday/cxs/{slug}/{tenant}/approot"

        try:
            approot = requests.get(url).json()
        except:
            return [None, None, None]

        if "facets" in approot.keys():
            facets = approot["facets"]

            matching = [f for f in facets if f in ["locationRegionStateProvince","locations", "Location_Country", "locationCountry", "primaryLocation", "Country","a","b","hiringCompany","locationHierarchy1"]]
            #if not matching:
            #    return [None, None, None]

            if matching:
                locationKey = matching[0]
            else:
                locationKey = None
        elif "tenantDefaultCountry" in approot.keys():
            descriptor = approot["tenantDefaultCountry"]["descriptor"]
            if descriptor != 'United States of America':
                return [None, None, None]

            locationKey = 'locations'
            locationVals = ["bc33aa3152ec42d4995f4791a106ed09"]

        try:

            for val in locationVals:
                rsp = self.getJobResponse(job_url, offset=0, locationKey=locationKey, locationVal=val)
                if "jobPostings" in rsp.keys():
                    print(rsp['total'])
                    return [rsp, locationKey, val]

        except Exception as e:
            print(e)


        return [None, None, None]

    def getFormattedJobs(self, company):

        slug = company.slug
        api_link = company.api_link
        path_split = api_link.split('/')
        tenant = path_split[-1]
        parsed = urllib.parse.urlparse(api_link)
        threading = HttpThreading(10, 10, 15)

        url = f"{parsed.scheme}://{parsed.netloc}/wday/cxs/{slug}/{tenant}/jobs"
        print(url)
        rsp, locationKey, locationVal = self.findLocation(url, slug, tenant, parsed.netloc)

        if rsp is None:
            return []

        #compute total number of pages and aggregate all results
        posts = rsp["jobPostings"]
        total = rsp["total"]
        pages = math.ceil(total / 20)

        #get all pages from api
        offsets = [x * 20 for x in range(1, pages + 1)]
        list(map(lambda x: posts.extend(self.getJobResponse(url, x,  locationKey=locationKey, locationVal=locationVal)['jobPostings']), offsets))

        #format api responses
        jobs = [self.formatJob(company, parsed, tenant, job) for job in posts]
        jobs = list(filter(lambda x: x is not None, jobs))

        #get all detail urls in parallel
        detail_urls = [x['url'] for x in jobs if x is not None]
        threading.executeGet(detail_urls)

        #update jobs with details strings
        jobs = list(map(lambda j: (j.update({'description': threading.getLastResponse(j['url'])}), j)[1], jobs))
        jobs = list(filter(lambda j: j['is_usa'] or j['is_remote'] is not None, jobs))
        print(len(jobs))
        return jobs