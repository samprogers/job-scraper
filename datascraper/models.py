from django.db import models
from django.contrib.postgres.fields import ArrayField

class Skill(models.Model):
    name = models.CharField(max_length=50)
    slug = models.CharField(max_length=50)
    category = models.CharField(max_length=50)
    subcategory = models.CharField(max_length=50)
    libraries = models.CharField(max_length=255)

    def getLibraries(self):
        return ",".split(self.libraries)

    def setLibraries(self, libraries: list):
        self.libraries = ",".join(libraries)
        return self

class Country(models.Model):
    name = models.CharField(max_length=50)
    slug = models.CharField(max_length=50)

class State(models.Model):
    name = models.CharField(max_length=50)
    abbreviation = models.CharField(max_length=2)
    slug = models.CharField(max_length=50)

class City(models.Model):
    name = models.CharField(max_length=50)
    state = models.ForeignKey(State, on_delete=models.CASCADE)

class Vendor(models.Model):
    name = models.CharField(max_length=50)
    slug = models.CharField(max_length=50)
    description = models.CharField(max_length=100)

class Company(models.Model):
    name = models.CharField(max_length=50)
    slug = models.CharField(max_length=50)
    api_link = models.URLField(null=True)
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, null=True)
    description = models.CharField(max_length=255)
    crawled_at = models.DateField(null=True)

class JobPosting(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    vendor_job_id = models.CharField(max_length=50, null=True)
    url = models.CharField(max_length=255)
    title = models.CharField(max_length=50)
    description = models.TextField(null=True)
    location = models.CharField(max_length=50,null=True)
    skills = models.CharField(max_length=255, default="")
    published_at = models.DateField(null=True)
    crawled_at = models.DateField()
    state = models.ForeignKey(State, on_delete=models.CASCADE, null=True)
    is_usa = models.BooleanField(default=False)
    is_remote = models.BooleanField(default=False)
    is_hybrid = models.BooleanField(default=False)

    def getSkills(self):
        return ",".split(self.skills)

    def setSkills(self, skills: list):
        skills = [x.lower() for x in skills]
        self.skills = ",".join(skills)
        return self


