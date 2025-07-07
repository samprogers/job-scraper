from django.core.management.base import BaseCommand, CommandError
from datascraper.services.api.googlecompanysearch import CompanyGoogleSearch
from datascraper.models import Company, JobPosting, Vendor
from datascraper.services.models.jobpostingwriter import JobPostingWriter
import datetime


class Command(BaseCommand):
    help = "Closes the specified poll for voting"

    #https://api.adzuna.com/v1/api/jobs/us/search/1?app_id=e52c7895&app_key=488c4bc623d5271dd8af90c1ba682e7f&&what=javascript%20developer&content-type=application/json&&results_per_page=100
    #curl -X POST -H "Content-Type: application/json" https://tamus.wd1.myworkdayjobs.com/wday/cxs/tamus/TEEX_External/jobs
    def handle(self, *args, **options):

        company_queries = [
            {"vendor": 5, "query": "site:myworkdayjobs.com"},
            {"vendor": 5, "query": "site:*.myworkdayjobs.com -www.myworkdayjobs.com"},
            {"vendor": 5, "query": "intitle:\"workday\" inurl:myworkdayjobs.com"},
            {"vendor": 5, "query": "site:myworkday.com inurl:wd3.myworkday.com"},
            {"vendor": 5, "query": "site:myworkday.com inurl:wd5.myworkday.com"},
            {"vendor": 5, "query": "site:myworkday.com inurl:wd10.myworkday.com"},
            {"vendor": 5, "query": "site:myworkday.com inurl:wd12.myworkday.com"},
            {"vendor": 5, "query": "inurl: myworkdayjobs.com careers"},
            {"vendor": 1, "query": "site:boards.greenhouse.io"},
            {"vendor": 1, "query": "site:boards.greenhouse.io \"jobs\""},
            {"vendor": 1, "query": "site:boards.greenhouse.io intitle:\"Careers]\""},
            {"vendor": 1, "query": "site:boards.greenhouse.io \"View Open Positions\""},
            {"vendor": 1, "query": "site:boards.greenhouse.io -jobs"},
            {"vendor": 1, "query": "site:boards.greenhouse.io \"remote jobs\""}
        ]
        job_queries = [
            'massachusetts',
            'remote',
            'boston',
            'greater boston',
            'devops+engineer',
            'solutions+software+engineer',
            'site+reliability+engineer',
            'lead+software+engineer',
            'principal+software+engineer',
            'staff+software+engineer',
            'software+architect'
        ]

        search = CompanyGoogleSearch()
        for query in company_queries:
            print(query['query'])
            vendor = Vendor.objects.get(id=query['vendor'])
            companies = search.getCompanies(query=query['query'])
            for company in companies:
                print(company['name'])
                self.writeCompany(company, vendor)

       # return
        jobs = search.getJobs(job_queries)
        writer = JobPostingWriter()
        writer.writeJobPostings(jobs)
        self.stdout.write(
            self.style.SUCCESS('Successfully ran google command')
        )