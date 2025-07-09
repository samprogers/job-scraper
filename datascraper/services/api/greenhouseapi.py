import requests
from datascraper.models import Vendor, State
import dateutil
from datascraper.services.parser.countryparser import CountryParser
from datascraper.util.formattedjobposting import FormattedJobPosting
from bs4 import BeautifulSoup

class GreenhouseApi:

    vendor = None

    def __init__(self):
        self.vendor = Vendor.objects.get(slug='greenhouse')
        self.states = State.objects.all()

    def isJobInUSA(self, job):
        parser = CountryParser()
        if job["location"]["name"] is None:
            return False

        job_location = job["location"]["name"]
        return parser.isLocationInUSA(job_location)

    def getFormattedJobs(self, company):

        jobs = []
        slug = company.slug
        url = f"https://boards-api.greenhouse.io/v1/boards/{slug}/jobs?content=true&pay_input_ranges=true"
        print(url)
        r = requests.get(url)

        parser = CountryParser()
        if r.status_code == 200:
            rsp = r.json()

            for job in rsp["jobs"]:
                vendor_job_id = job["id"]
                title = job["title"]
                job_company = job["company_name"]
                content = job["content"]
                location = job["location"]["name"]
                is_usa = self.isJobInUSA(job) if location is not None else False
                is_remote = True if parser.isRemote(location) or parser.isRemote(title) else False
                is_hybrid = parser.isRemote(location) if location is not None else False
                state = parser.getState(location) if location is not None else None

                published_at = job["first_published"] if "first_published" in job.keys() and job["first_published"] is not None else None


                if self.isJobInUSA(job):
                    if published_at is not None:
                        parsed_published_at = dateutil.parser.parse(published_at)
                    else:
                        parsed_published_at = None
                    #datetime.datetime.strftime(parsed_published_at, "%Y-%m-%dT%H:%M:%S")

                    formatted = FormattedJobPosting(
                        url=job["absolute_url"],
                        title=title,
                        description=content,
                        vendor_job_id=vendor_job_id,
                        company={"name": company.name, "slug": company.slug},
                        location=location,
                        vendor=self.vendor,
                        published_at=parsed_published_at,
                        state=state,
                        is_usa=is_usa,
                        is_hybrid=is_hybrid,
                        is_remote=is_remote
                    )

                    if is_usa or is_remote:
                        jobs.append(formatted)
                        print(f"{job_company} - {title} - {location}")


        else:
            print(f"{company.slug} - not found or no jobs")

        return jobs