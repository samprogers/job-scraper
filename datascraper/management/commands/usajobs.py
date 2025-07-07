from django.core.management.base import BaseCommand, CommandError
from datascraper.models import Company
import requests
from django.conf import settings

class Command(BaseCommand):
    help = "Closes the specified poll for voting"


    def getAllCodes(self):
        all_codes = []
        headers = {'Host': 'data.usajobs.gov', 'Authorization-Key': settings.USAJOBS_API_KEY, 'User-Agent': settings.USAJOBS_EMAIL_ADDRESS}
        r = requests.get('https://data.usajobs.gov/api/codelist/agencysubelements', headers=headers)
        content = r.json()

        for code in content['CodeList']:
            print(code.keys())
            values = code['ValidValue']
            for value in values:
                all_codes.append(value['Code'])
        return all_codes


    def getCurrentCompanies(self):
        return Company.objects.raw('SELECT * FROM datascraper_company where slug = "airbnb" order by slug asc')

    def handle(self, *args, **options):
        return
        codes = self.getAllCodes()

        headers = {'Host': 'data.usajobs.gov', 'Authorization-Key': settings.USAJOBS_API_KEY, 'User-Agent': settings.USAJOBS_EMAIL_ADDRESS}
        for code in codes:
            print(code)
            url = f"https://data.usajobs.gov/api/search?JobCategoryCode={code}"
            r = requests.get(url, headers=headers)
            content = r.json()

            items = content['SearchResult']['SearchResultItems']
            print(items)
            print(len(items))
            for result in items:
                job = result['MatchedObjectDescriptor']
                orgname = job['OrganizationName']
                title = job['PositionTitle']
                published_at = job['PublicationStartDate']
                print(orgname, title, published_at)




        self.stdout.write(
            self.style.SUCCESS('Successfully ran usajobs command')
        )