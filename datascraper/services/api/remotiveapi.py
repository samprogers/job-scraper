import json, requests
from datascraper.models import Vendor, Skill
import sys,datetime,dateutil
from datascraper.services.parser.stringextracter import StringExtracter
from datascraper.util.formattedjobposting import FormattedJobPosting

class RemotiveApi:

    vendor = None

    def __init__(self):
        self.vendor = Vendor.objects.get(slug='remotive')

    def getFormattedJobs(self):

        jobs = []
        parser = StringExtracter()
        url = f"https://remotive.com/api/remote-jobs"
        r = requests.get(url)
        content = r.json()

        all_skills = []

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
            formatted = FormattedJobPosting(
                url=url,
                title=title,
                description=description,
                vendor_job_id=vendor_job_id,
                company={"slug": company_name, "name": company_name },
                location=location,
                vendor=self.vendor,
                published_at=dateutil.parser.parse(published_at),
                state=state,
                is_usa=is_usa,
                is_remote=is_remote,
                is_hybrid=parser.isHybrid(location) if location is not None else False
            )

            if len(languages) > 0:
                all_skills.extend(languages)
                formatted.skills = languages

            jobs.append(formatted)

        #filter by USA or worldwide
        #for sk in all_skills:
        #    exist = Skill.objects.filter(slug=sk).exists()
        #    if not exist:
        #        new = Skill(
        #            slug=sk,
        #            name=sk,
        #            category="Programming Language",
        #            subcategory="General-Purpose",
        #            libraries=""
        #        )
        #        print(sk)
        #        new.save()


        return jobs