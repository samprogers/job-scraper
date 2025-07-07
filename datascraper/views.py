import os, re, datetime, sys
from dataclasses import fields

from django.shortcuts import render
from django.http import HttpResponse, FileResponse, HttpResponsePermanentRedirect
from django.template.loader import render_to_string, get_template
from django.conf import settings
from datascraper.models import Company, JobPosting
from datascraper.documents import JobPostingDocument
from elasticsearch_dsl import Document, Q
from operator import or_
from functools import reduce

def generate_search_query():

    # degrees / mental health, speaker, advocate, case manager / exclude RN positions LICSW bi-lingual / newest job postings first

    skills = ["php", "symfony", "python", "django", "terraform", "kubernetes", "prometheus", "jenkins", "ci/cd", "lambda", "ec2", "docker", "containerization", "serverless", "redis", "SAML", "microservices", "sqs", "sns", "rds", "mysql", "github actions"]
    #skills = ["php"]
    degrees = ['masters public health', 'masters human services']
    nots = ['manager', 'director', 'node.js', '.NET','nodeJS','C#','C++','Front-End','frontend','ruby','data science','machine learning','ML','java','robotic','embedded']
    #locations = ['Remote', 'US', 'USA', 'Massachusetts','MA']
    titles = ["senior software engineer", "devops engineer", "solutions software engineer","principal software engineer", "lead software engineer", "staff software engineer"]
    #titles = ['senior software engineer']

    skill_musts = [Q("multi_match", query=x, fields=["title^2","content"], fuzziness=2, operator="or") for x in skills]
    title_musts = [Q("multi_match", query=x, fields=["title^2", "content"], fuzziness=2, operator="or") for x in titles]
    must_nots = [Q("multi_match", fields=["content"], query=x) for x in nots]
    #location_match = [Q("match", location=x) for x in locations]


    all_ors = reduce(or_, title_musts + skill_musts)  # THE MAGIC!

    #title_bool = Q(
    #    "bool",
    #    must=title_ors,
        #should=Q("range", published_at={"gte": "2025-06-01"}),
   #     minimum_should_match = 1
   # )
   # skill_bool = Q(
   #     "bool",
    #    must=skill_ors,
        #should=Q("range", published_at={"gte": "2025-06-01"}),
   #     minimum_should_match = 1,
   #     boost=1.0
   # )

    final_qry = Q(
        "bool",
        must=Q("range", published_at={"gte": "2025-06-22"}) & Q("match", is_usa=True) & (Q('match', is_remote=True) | Q('match', state="MA")),
        should=Q("dis_max", queries=title_musts + skill_musts, tie_breaker=0.7),
        #must_not=Q("dis_max", queries=must_nots, tie_breaker=0.7),
        #must_not=[Q("multi_match", query="manager",fields=["title^2","content"], fuzziness=2, operator="or"), Q("match", content="node"), Q("match", title="director")],
        #should=Q("range", published_at={"gte": "2025-06-01"}),
        filter=Q("bool", must_not=reduce(or_, must_nots))
        #minimum_should_match = 1
    )

    return final_qry


def index(request):
    jobs = []

    qry = generate_search_query()
    dsl = JobPostingDocument.search().query(qry)
    #response = search.to_queryset()

    for job in dsl[0:150].execute():

        jobs.append(job)


    #for job in JobPosting.objects.raw("SELECT * FROM datascraper_jobposting where published_at >= '2025-05-20' order by published_at desc"):
    #    company = job.company
    #    key = f"{company.slug}"
    #    if key not in grouped_jobs:
    #        grouped_jobs[key] = []

    #    grouped_jobs[key].append(job)

    return render(request, 'datascraper/index.html', {'jobs': jobs})