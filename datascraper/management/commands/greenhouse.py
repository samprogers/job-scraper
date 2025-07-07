from django.core.management.base import BaseCommand, CommandError
from datascraper.services.api.greenhouseapi import GreenhouseApi
from datascraper.models import Company, JobPosting
from datascraper.services.models.jobpostingwriter import JobPostingWriter
import datetime

class Command(BaseCommand):
    help = "Closes the specified poll for voting"

    def getCurrentCompanies(self):
        #Company.objects.search()
        now = datetime.datetime.now()
        nowfmt = now.strftime("%Y-%m-%d")
        return Company.objects.raw(f"SELECT * FROM datascraper_company where vendor_id = 1 and (crawled_at < '{nowfmt}' or crawled_at is null) order by slug asc")

    def handle(self, *args, **options):
        api = GreenhouseApi()
        companies = self.getCurrentCompanies()
        writer = JobPostingWriter()

        for company in companies:

            jobs = api.getFormattedJobs(company)
            writer.writeJobPostings(jobs)

            company.crawled_at = datetime.datetime.now()
            company.save()

        self.stdout.write(
            self.style.SUCCESS('Successfully ran greenhouse command')
        )