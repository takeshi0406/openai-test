import arxiv
from newschatbot.valueobjects import Article

class ArxivClient:
    def __init__(self):
        pass

    def fetch(self):
        result = arxiv.Search(
            query='(cat:"cs.ai" OR cat:"cs.cv") AND (abs:"estate" OR abs:"floorplan")',
            max_results=20,
            sort_by=arxiv.SortCriterion.SubmittedDate,
            sort_order=arxiv.SortOrder.Descending,
        ).results()
        return [Article(title=x.title, url=x.entry_id, published=x.published, content=x.summary) for x in result]