from datascraper.models import Company, JobPosting, Vendor
import datetime, sys

class JobPostingWriter:

    existing_jobs = {}
    existing_companies = {}

    def getCompany(self, slug):
        return Company.objects.get(slug=slug)

    def getSlug(self, name):
        chars = [' ', '%20', ',', '.','(',')',"'"]
        for char in chars:
            name = name.replace(char, '')

        return name

    def writeCompany(self, company, vendor):
        company_name = company['slug']
        slug = self.getSlug(company_name)
        if slug in self.existing_companies.keys():
            return self.existing_companies[slug]

        exist = Company.objects.filter(slug=slug).exists()
        if not exist:
            #print("adding company " + slug)
            new = Company(name=company['name'], slug=slug,description="",vendor=vendor)
            if "api_link" in company.keys():
                new.api_link = company['api_link']

            new.save()
            self.existing_companies[slug] = new

            return new
        else:

            obj = Company.objects.get(slug=slug)
            obj.slug = slug
            obj.name = company['name']
            obj.save()

            self.existing_companies[slug] = obj
            #print("updating company " + obj.slug)
            return obj

    def getJob(self, job):

        url = job["url"]
        location = job["location"]
        published_at = job["published_at"]
        vendor_job_id = job["vendor_job_id"]
        job_company = job["company"]
        vendor = job["vendor"]
        title = job["title"]
        description = job["description"]
        state = job["state"]
        is_remote = job["is_remote"]
        is_usa = job["is_usa"]

        now = datetime.datetime.now()
        company = self.writeCompany(job_company, vendor)
        exist = JobPosting.objects.filter(vendor=vendor.id, company=company.id, title=title).exists()
        uniq_hash = hash(title + job_company['name'])

        if not exist and title:
            new = JobPosting(
                url=url,
                title=title,
                description=description,
                location=location,
                published_at=published_at,
                crawled_at=now,
                company=company,
                vendor_job_id=vendor_job_id,
                vendor=vendor,
                is_usa=is_usa,
                is_remote=is_remote
            )

            if state is not None:
                new.state = state

            #print(self.existing_elements)
            if uniq_hash in self.existing_jobs.keys():
                self.existing_jobs[uniq_hash] = new
                return None
            else:
                self.existing_jobs[uniq_hash] = new
                return new, True, False
        else:
            #print("UDPATE!")
            posting = JobPosting.objects.get(vendor=vendor.id, company=company.id, title=title)
            #print(posting.id)
            #print(company)

            posting.url = job["url"]
            #print(job["url"])
            posting.published_at = job["published_at"]
            posting.location = job["location"]
            posting.description = job["description"]
            posting.company = company
            posting.is_usa = is_usa
            posting.is_remote = is_remote

            if state is not None:
                posting.state = state

            self.existing_jobs[uniq_hash] = posting
            return posting, False, True


    def writeJobPostings(self, jobs):
        self.existing_jobs = {}
        self.existing_companies = {}

        tuples = list(map(lambda j: self.getJob(j), jobs))
        new = [j[0] for j in tuples if j is not None and j[1] is True]
        update = [j[0] for j in tuples if j is not None and j[2] is True]

        JobPosting.objects.bulk_create(new, batch_size=50)

        #update = list(map(lambda j: (j.refresh_from_db(), j)[1], update))
        #new = list(map(lambda j: (j.refresh_from_db(), j)[1], update))

        JobPosting.objects.bulk_update(update, ['url', 'published_at', 'location', 'description', 'company', 'is_usa', 'is_remote', 'state'], batch_size=50)
        print(f"created {len(new)} jobs")
        print(f"updated {len(update)} jobs")

