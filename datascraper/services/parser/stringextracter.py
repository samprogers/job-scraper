import sys, re, html
from datascraper.models import State, City, Skill


class StringExtracter:

    def isRemote(self, location_string):
        return 'remote' in location_string.lower() if location_string is not None else False

    def isHybrid(self, location_string):
        return 'hybrid' in location_string.lower() if location_string is not None else False

    def getSkills(self, text):
        library_skills = []
        exclude = ["R","C"]
        skills = Skill.objects.all()
        text = html.unescape(text)

        all_skills = [x.name for x in skills]

        #add to library_skills and format
        [library_skills.extend(x.libraries.split(',')) for x in skills if x.libraries != '']
        library_skills = [x.strip() for x in library_skills]
        all_skills = all_skills + library_skills

        escaped_skills = [f"{re.escape(lang)}" for lang in all_skills]
        exclusion_pattern = ''.join([rf'(?!(?:{re.escape(ex)}\b))' for ex in exclude])
        pattern = rf'(?<!\w){exclusion_pattern}({"|".join(escaped_skills)})(?!\w)'

        flags = re.IGNORECASE
        matches = re.findall(pattern, text, flags)

        lower_matches = [x.lower() for x in matches]
        return list(set(lower_matches))

    def getState(self, location_string):

        if location_string is None:
            return None

        all_states = State.objects.all()
        all_cities = City.objects.all()
        abbreviations = [x.abbreviation for x in all_states]
        names = [x.name for x in all_states]

        abbr_or = '|'.join(abbreviations)
        names_or = '|'.join(names)

        abbr_match = re.findall(re.compile(f"(\b{abbr_or}\b)"), location_string)
        name_match = re.findall(re.compile(f"(\b{names_or}\b)"), location_string)
        if abbr_match:
            abbr = abbr_match[0]
            exist =  State.objects.filter(abbreviation=abbr).exists()
            return State.objects.get(abbreviation=abbr) if exist else None
        elif name_match:
            name = name_match[0]
            exist = State.objects.filter(name=name).exists()
            return State.objects.get(name=name) if exist else None

        return None

    def isLocationInUSA(self, location_string: str) -> bool:
        country_strings = ['United States', 'US', 'USA', 'United States of America', 'U.S', 'Anywhere', 'Northern America', 'Worldwide', 'Nationwide', 'Global','North America']

        all_states = State.objects.all()
        abbreviations = [x.abbreviation for x in all_states]
        names = [x.name for x in all_states]


        abbr_or = '|'.join(abbreviations)
        names_or = '|'.join(names)
        country_or = '|'.join(country_strings)

        abbr_match = re.findall(re.compile(f"({abbr_or})"), location_string)
        name_match = re.findall(re.compile(f"({names_or})"), location_string)
        country_match = re.findall(re.compile(f"({country_or})"), location_string)
        if name_match or abbr_match or country_match:
            return True

        #all_cities = City.objects.all()
        #names = [x.name for x in all_cities]
        #names_or = '|'.join(names)
        #name_match = re.findall(re.compile(f"({names_or})"), location_string)
        #if len(name_match) == 1:
        #    return True

        return False


