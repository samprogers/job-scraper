
# documents.py
import sys
from django_elasticsearch_dsl import Document, fields
from django_elasticsearch_dsl.registries import registry
from .models import JobPosting, Company, Vendor

@registry.register_document
class JobPostingDocument(Document):

    state = fields.KeywordField(attr='state.abbreviation')
    company = fields.KeywordField(attr='company.slug')
    vendor = fields.KeywordField(attr='vendor.slug')

    class Index:
        # Name of the Elasticsearch index
        name = 'jobs'
        # See Elasticsearch Indices API reference for available settings
        settings = {'number_of_shards': 1,
                    'number_of_replicas': 0}

    class Django:
        model = JobPosting # The model associated with this Document

        # The fields of the model you want to be indexed in Elasticsearch
        fields = [
            'vendor_job_id',
            'title',
            'description',
            'url',
            'published_at',
            'crawled_at',
            'location',
            'is_usa',
            'is_remote',
            'is_hybrid',
        ]

    def get_queryset(self):
        return super(JobPostingDocument, self).get_queryset().select_related(
            'company',
            'vendor',
        )

    def prepare_company_with_related(self, jobposting, related_to_ignore):
        if jobposting.company is not None and jobposting.company != related_to_ignore:
            return jobposting.company.slug
            #return {
            #    'name': jobposting.company.name,
            #    'slug': jobposting.company.slug,
            #}

    def prepare_vendor_with_related(self, jobposting, related_to_ignore):
        if jobposting.vendor is not None and jobposting.vendor != related_to_ignore:
            return jobposting.vendor.slug
            #return {
            #    'name': jobposting.vendor.name,
            #    'slug': jobposting.vendor.slug,
            #}