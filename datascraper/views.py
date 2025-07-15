import os, re, datetime, sys, html
from dataclasses import fields

from django.shortcuts import render
from django.http import HttpResponse, FileResponse, HttpResponsePermanentRedirect
from django.template.loader import render_to_string, get_template
from django.conf import settings
from datascraper.services.parser.htmlparser import HTMLParser
from datascraper.models import Company, JobPosting, State,Skill
from datascraper.documents import JobPostingDocument
from elasticsearch_dsl import Document, Q
from operator import or_, and_
from functools import reduce
from datetime import date, timedelta

def generate_search_query(params: dict):

    # degrees / mental health, speaker, advocate, case manager / exclude RN positions LICSW bi-lingual / newest job postings first
    skill_musts = []
    musts = []

    now = datetime.datetime.now()
    skills = params['skills']
    titles = params['titles']
    state = params['state']
    days = params['days']
    nots = params['ex_keywords']
    term_nots = params['ex_skills']

    start_date = now - timedelta(days=days)
    title_musts = [Q("multi_match", query=val, fields=["title"], fuzziness=2, operator="or", boost=5 if key == 0 else 2) for key,val in enumerate(titles)]
    not_keywords = [Q("multi_match", query=val, fields=["title"], fuzziness=2, operator="or") for val in nots]

    if len(skills) >= 2:
        primary_skill = Q('term', skills={"value": skills[0], "boost": 5})
        secondary_skill = Q('term', skills={"value": skills[1], "boost": 2})
        rest_of_skills = skills[2:]
    else:
        primary_skill = Q('term', skills={"value": skills[0], "boost": 5})
        secondary_skill = Q('term', skills={"value": skills[0], "boost": 2})
        rest_of_skills = skills[1:-1]

    if len(rest_of_skills) > 0:
        skill_musts = [Q("term", skills={"value": x, "boost": 1.5}) for x in rest_of_skills]

    skills_qry = Q("terms_set", skills={"terms": skills, "minimum_should_match": 1})
    final_qry = Q(
        "bool",
        must=title_musts + [skills_qry],
        should=[primary_skill, secondary_skill] + skill_musts,
        filter=Q("range", published_at={"gte": start_date.strftime('%Y-%m-%d')}) & Q("match", is_usa=True) & (Q('match', is_remote=True) | Q('match', state=state)),
        must_not=[Q("terms_set", skills={"terms": term_nots, "minimum_should_match": 1})] + not_keywords,
        #minimum_should_match=1
    )

    return final_qry


def index(request):
    skills = [x.slug for x in Skill.objects.all()]
    states = [x.abbreviation for x in State.objects.all()]
    params = {
        'skills': request.GET.get('skills').split(',') if request.GET.get('skills') else None,
        'titles': request.GET.get('titles').split(',') if request.GET.get('titles') else None,
        'ex_skills': request.GET.get('exclude-skills').split(',') if request.GET.get('exclude-skill') else [],
        'ex_keywords': request.GET.get('exclude-keywords').split(',') if request.GET.get('exclude-keywords') else [],
        'state': request.GET.get('state') if request.GET.get('state') else "MA",
        'days': int(request.GET.get('days-old', 14)),
    }

    print(params['skills'])
    print(params['state'])

    jobs = []
    parser = HTMLParser()
    total_results = 0

    if params['skills'] is not None:
        qry = generate_search_query(params)
        dsl = JobPostingDocument.search().query(qry)
        total_results = dsl.count()
        print(dsl.to_dict())
        print(total_results)


        for job in dsl[0:150].execute():
            job.print_skills = ','.join(job.skills)

            if job.description is not None:
                job.description = parser.cleanHTMLString(job.description)
            jobs.append(job)

    #for job in JobPosting.objects.raw("SELECT * FROM datascraper_jobposting where published_at >= '2025-05-20' order by published_at desc"):
    #    company = job.company
    #    key = f"{company.slug}"
    #    if key not in grouped_jobs:
    #        grouped_jobs[key] = []

    #    grouped_jobs[key].append(job)

    return render(request, 'datascraper/index.html', {'jobs': jobs, 'params': params, 'total': total_results, 'size': len(jobs), 'states': states, 'skills': skills })