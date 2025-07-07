import json, requests

from pip._internal import locations

from datascraper.models import Vendor
import sys,datetime,dateutil
from datascraper.services.parser.countryparser import CountryParser


class RemotiveApi:

    vendor = None

    def __init__(self):
        self.vendor = Vendor.objects.get(slug='remotive')

    def getFormattedJobs(self):

        jobs = []
        parser = CountryParser()
        url = f"https://remotive.com/api/remote-jobs"
        r = requests.get(url)
        content = r.json()

        for job in content['jobs']:
            url = job['url']
            vendor_job_id = job['id']
            title = job['title']
            company_name = job['company_name']
            languages = job['tags']
            published_at = job['publication_date']
            location = job['candidate_required_location']
            description = job['description']
            is_usa = parser.isLocationInUSA(location) if location is not None else False
            is_remote = parser.isRemote(location) or parser.isRemote(title) or parser.isRemote(description)

            if not is_usa:
                continue

            state = parser.getState(location)
            formatted = {
                "url": url,
                "title": title,
                "company": {"slug": company_name, "name": company_name },
                "vendor": self.vendor,
                "location": location,
                "vendor_job_id": vendor_job_id,
                "programming_languages": ','.join(languages),
                "published_at": dateutil.parser.parse(published_at),
                'description': description,
                'is_usa': is_usa,
                'is_remote': is_remote,
                'is_hybrid': parser.isHybrid(location) if location is not None else False,
                'state': state
            }

            jobs.append(formatted)

        #filter by USA or worldwide
        return jobs