from django.core.management.base import BaseCommand, CommandError
from datascraper.services.api.adzunaapi import AdzunaApi
from datascraper.models import Company, JobPosting
import sys, datetime, requests, dateutil
import nltk
from nltk import pos_tag, word_tokenize
from datascraper.models import State, City
import csv

from datascraper.services.parser.stringextracter import CountryParser
import json

class Command(BaseCommand):
    help = "Closes the specified poll for voting"

    #https://api.adzuna.com/v1/api/jobs/us/search/1?app_id=e52c7895&app_key=488c4bc623d5271dd8af90c1ba682e7f&content-type=application/json&results_per_page=100&what=php+software

    def get_tokens(self, location):
        return pos_tag(word_tokenize(location))

    def handle(self, *args, **options):
        locations = []
        nltk.download('punkt_tab')
        nltk.download('averaged_perceptron_tagger_eng')
        parser = CountryParser()

        postings = JobPosting.objects.all()
        for posting in postings:

            location = posting.location
            title = posting.title
            description = posting.description
            if location is None:
                continue

            state = parser.getState(location)
            is_usa = parser.isLocationInUSA(location)

            is_hybrid = parser.isRemote(location)

            remote_location = parser.isRemote(location) if location is not None else False
            remote_title = parser.isRemote(title) if title is not None else False
            #remote_desc = parser.isRemote(description) if description is not None else False
            is_remote = True if remote_location or remote_title else False

            posting.is_usa = is_usa
            posting.is_remote = is_remote
            posting.is_hybrid = is_hybrid
            if state is not None:
                posting.state = state

            posting.save()

            if is_remote:
                print(location)
                print(title)

        self.stdout.write(
            self.style.SUCCESS('Successfully ran greenhouse command')
        )