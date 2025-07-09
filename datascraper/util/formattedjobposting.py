from datascraper.models import Vendor, State, Company
class FormattedJobPosting:

    def __init__(
        self,
        url: str=None,
        title: str=None,
        description: str = None,
        location: str=None,
        company: dict=None,
        vendor: Vendor=None,
        vendor_job_id: str=None,
        published_at=None,
        state: State=None,
        is_usa: bool=False,
        is_remote: bool=False,
        is_hybrid: bool=False
    ):
        self.url = url
        self.title = title
        self.company = company
        self.vendor = vendor
        self.vendor_job_id = vendor_job_id
        self.published_at = published_at
        self.description = description
        self.location = location
        self.state = state
        self.is_usa = is_usa
        self.is_remote = is_remote
        self.is_hybrid = is_hybrid
