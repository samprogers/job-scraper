FROM python:3.13
RUN apt-get update
RUN apt-get install jq git npm -y

RUN /usr/local/bin/python -m ensurepip --upgrade
#RUN /usr/local/bin/pip install poetry Django djangorestframework semver djangorestframework-recursive
RUN /usr/local/bin/pip install poetry pre-commit
#RUN mkdir -p /var/task/snyk-code-review-exercise/.venv

ADD . /var/task/job-scraper
RUN /usr/local/bin/poetry config virtualenvs.path /var/task/job-scraper/.venv

WORKDIR /var/task/job-scraper
ENV VENV_PATH=/var/task/job-scraper/.venv/bin/python

RUN npm config set prefix /usr
#RUN npm -g install serverless

#fix pre-commit issues on container
#RUN git config --local core.fileMode false

COPY . /var/task/job-scraper
#RUN source /var/task/job-scraper/elastic-start-local/.env

#CMD ["/var/task/snyk-code-review-exercise/start.sh"]
EXPOSE 8000
