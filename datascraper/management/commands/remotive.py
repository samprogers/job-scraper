from django.core.management.base import BaseCommand, CommandError
from datascraper.services.api.remotiveapi import RemotiveApi
from datascraper.services.models.jobpostingwriter import JobPostingWriter
from datascraper.models import Company, JobPosting
import datetime, requests
from django.conf import settings


class Command(BaseCommand):
    help = "Closes the specified poll for voting"

    def checkCompany(self, company_name):
        slug = company_name.lower().replace(" ", "").replace(",", "").replace(".", "").replace("%20", "").strip()
        exist = Company.objects.filter(slug=slug).exists()
        if not exist:
            company = Company(slug=slug, name=company_name)
            company.save()
        else:
            company = Company.objects.get(slug=slug)

        return company


    def handle(self, *args, **options):
        api = RemotiveApi()
        jobs = api.getFormattedJobs()
        writer = JobPostingWriter()
        writer.writeJobPostings(jobs)
        self.stdout.write(
            self.style.SUCCESS('Successfully ran remotive command')
        )