from .base import *


__all__ = ['Pagination', 'Result', 'Search', 'BaseParam', 'Item', 'Recipe']


class Pagination(Model):
    __repr_attrs__ = ['results_total']

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
    __repr_attrs__ = ['pagination', 'results']
    pagination: Pagination = Elem('Pagination')
    results: Result = ElemList('Results')


class BaseParam(Index, Model):
    id: int = Elem('ID')
    name: str = Elem('Name')
    description: str = Elem('Description')
    url: str = Elem('Url')


class Item(Index, Model):
    id: int = Elem('ID')
    name: str = Elem('Name')
    description: str = Elem('Description')
    icon: str = Elem('Icon')

    params: BaseParam = ElemGroup('BaseParam*')[0:5]


class Recipe(Index, Model):
    id: int = Elem('ID')
    name: str = Elem('Name')
