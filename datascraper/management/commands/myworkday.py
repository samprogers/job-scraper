from django.core.management.base import BaseCommand, CommandError
from datascraper.services.api.myworkdayapi import MyWorkdayApi
from datascraper.models import Company, JobPosting
from datascraper.services.models.jobpostingwriter import JobPostingWriter
import datetime

class Command(BaseCommand):
    help = "Closes the specified poll for voting"

    def getCurrentCompanies(self):
        #Company.objects.search()
        now = datetime.datetime.now()
        nowfmt = now.strftime("%Y-%m-%d")
        return Company.objects.raw(f"SELECT * FROM datascraper_company where api_link is not null and vendor_id = 5 and crawled_at < '2025-07-14' group by api_link order by slug asc ")

    def handle(self, *args, **options):
        api = MyWorkdayApi()
        companies = self.getCurrentCompanies()
        writer = JobPostingWriter()

        for company in companies:
            print(company.name)
            print(company.api_link)
            print(company.id)
            jobs = api.getFormattedJobs(company)
            now = datetime.datetime.now()

            writer.writeJobPostings(jobs)

            company.crawled_at = now
            company.save()

        self.stdout.write(
            self.style.SUCCESS('Successfully ran greenhouse command')
        )