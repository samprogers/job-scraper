from django.core.management.base import BaseCommand, CommandError
from datascraper.services.api.adzunaapi import AdzunaApi
from datascraper.models import Company, JobPosting
from datascraper.services.parser.stringextracter import StringExtracter
import sys, datetime, requests, dateutil, re, html, string, csv, time
import nltk, spacy
from nltk import pos_tag, word_tokenize
from datascraper.models import State, City, Skill
from rapidfuzz import process, fuzz
from bs4 import BeautifulSoup
import html2text
import pandas as pd


class Command(BaseCommand):
    help = "Closes the specified poll for voting"

    def clean_html(self, text):
        soup = BeautifulSoup(html.unescape(text), "html.parser")
        for script in soup(["script", "style", 'a','title','head']):
            script.decompose()

        elements = [x.get_text() if x.get_text() != "" else " " for x in soup.find_all() if x.get_text() != ""]
        return '\n'.join(elements)

    def remove_html_tags(self, text):
        """Remove html tags from a string"""

        soup = BeautifulSoup(text, "html.parser")
        for script in soup(["script", "style"]):
            script.decompose()


        content = [x.attrs['content'] if x.get_text() == "" and "content" in x.attrs.keys() else soup.get_text() for x in soup.find_all()]
        return "\n".join(content).strip()

    def extract_skills_regex(self, text):
        exclude = ["R","C"]
        skills = Skill.objects.all()
        text = self.clean_html(text)

        library_skills = []
        all_skills = [x.name for x in skills]

        #add to library_skills
        [library_skills.extend(x.libraries.split(',')) for x in skills if x.libraries != '']
        library_skills = [x.strip() for x in library_skills]
        all_skills = all_skills + library_skills
        #print(all_skills)


        escaped_languages = [f"{re.escape(lang)}" for lang in all_skills]
        exclusion_pattern = ''.join([rf'(?!(?:{re.escape(ex)}\b))' for ex in exclude])
        pattern = rf'(?<!\w){exclusion_pattern}({"|".join(escaped_languages)})(?!\w)'
        #pattern = rf'\b{exclusion_pattern}({"|".join(escaped_languages)})\b'
        #print(pattern)

        flags = re.IGNORECASE
        matches = re.findall(pattern, text, flags)
        if 'PHP' in matches:
            print(matches)

        lower_matches = [x.lower() for x in matches]
        return list(set(lower_matches))

    def extract_skills_skillner(self, skill_extractor, text):

        elements = []
        soup = BeautifulSoup(html.unescape(text), "html.parser")
        for script in soup(["script", "style", 'a','title','head']):
            script.decompose()

        elements = [x.get_text() if x.get_text() != "" else " " for x in soup.find_all() if x.get_text() != ""]
        text = '\n'.join(elements)
        #text = text.replace("·", " ")
        #text = text.encode('ascii', errors='ignore').decode('ascii')
        #print(text)

        #skill_extractor = SkillExtractor(nlp, SKILL_DB, PhraseMatcher)
        annotations = skill_extractor.annotate(text)
        print(skill_extractor.describe(annotations).display())
        sys.exit()

        full_match = [x['doc_node_value'] for x in annotations['results']['full_matches'] if x['score'] >= 1]
        part_match = [x['doc_node_value'] for x in annotations['results']['ngram_scored'] if x['type'] >= 'fullUni']
        return list(set(full_match + part_match))

    def extract_onet_skills(self, nlp, text, known_skills):
        doc = nlp(text.lower())
        found = set()

        # Token-based matching (simple version)
        for chunk in doc.noun_chunks:
            phrase = chunk.text.strip()
            if phrase in known_skills:
                found.add(phrase)

        # Optional: include individual token checks
        for token in doc:
            if token.text in known_skills:
                found.add(token.text)

        return sorted(found)

    def get_skills(self, df, key):
        return df[key].str.lower().unique().tolist()

    def handle(self, *args, **options):

        extractor = StringExtracter()
        postings = JobPosting.objects.raw("SELECT * FROM datascraper_jobposting ")

        for posting in postings:
            url = posting.url
            description = posting.description
            if description is None or description == "":
                continue

            print(posting.title)
            print(url)
            description = posting.description

            found_skills = extractor.getSkills(description)
            print("Extracted Skills:")
            for skill in found_skills:
                print("-", skill)

            if len(found_skills) > 1:
                posting.setSkills(found_skills)
                posting.save()

        self.stdout.write(
            self.style.SUCCESS('Successfully ran greenhouse command')
        )