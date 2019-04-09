from xivapi.models import Model, Elem
from typing import Dict

__all__ = ['Pagination', 'Result', 'Search', 'Item', 'Recipe']


class Pagination(Model):
    page: int = Elem('Page')
    page_next: int = Elem('PageNext')
    page_prev: int = Elem('PagePrev')
    page_total: int = Elem('PageTotal')
    results: int = Elem('Results')
    results_per_page: int = Elem('ResultsPerPage')
    results_total: int = Elem('ResultsTotal')


class Result(Model):
    id: int = Elem('ID')
    name: str = Elem('Name')
    icon: str = Elem('Icon')
    url: str = Elem('Url')

    async def get(self):
        t = Index.types[self.url.split('/')[1].lower()]
        async with self.client.session.get(f'https://xivapi.com{self.url}') as r:
            return t(self.client, **await r.json())


class Search(Model):
    pagination: Pagination = Elem('Pagination')
    results: [Result] = Elem('Results')


class Index:
    """
    Represents something that can be accessed at a /index/id endpoint.
    Subclassing this simply adds it to a dict so it can be looked up later.
    This lets Result.get() work for example.
    Could add more in the future
    """
    types: Dict[str, type] = {}

    @classmethod
    def __init_subclass__(cls):
        super().__init_subclass__()
        Index.types[cls.__name__.lower()] = cls


class Item(Index, Model):
    id: int = Elem('ID')
    name: str = Elem('Name')
    description: str = Elem('Description')
    icon: str = Elem('Icon')


class Recipe(Index, Model):
    id: int = Elem('ID')
    name: str = Elem('Name')
