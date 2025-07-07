from django.core.management.base import BaseCommand, CommandError
from datascraper.services.api.adzunaapi import AdzunaApi
from datascraper.models import Company, JobPosting
from datascraper.services.models.jobpostingwriter import JobPostingWriter
import sys, datetime, requests, dateutil

class Command(BaseCommand):
    help = "Closes the specified poll for voting"

    #https://api.adzuna.com/v1/api/jobs/us/search/1?app_id=e52c7895&app_key=488c4bc623d5271dd8af90c1ba682e7f&content-type=application/json&results_per_page=100&what=php+software

    def writeCompany(self, company, vendor):

        exist = Company.objects.filter(slug=company['slug']).exists()
        if not exist:
            print("adding company " + company['slug'])
            new = Company(name=company['name'], slug=company['slug'],description="",vendor=vendor)
            new.save()
            return new
        else:

            obj = Company.objects.get(slug=company['slug'])
            obj.slug = company['slug']
            obj.name = company['name']
            obj.save()

            print("updating' company " + obj.slug)
            return obj


    def handle(self, *args, **options):
        job_queries = [
            'software+engineer',
            'devops+engineer',
            'solutions+software+engineer',
            'lead+software+engineer',
            'principal+software+engineer',
            'staff+software+engineer',
            'software+architect'
        ]

        api = AdzunaApi()
        writer = JobPostingWriter()

        for query in job_queries:
            jobs = api.getFormattedJobs(query)
            writer.writeJobPostings(jobs)

        self.stdout.write(
            self.style.SUCCESS('Successfully ran greenhouse command')
        )