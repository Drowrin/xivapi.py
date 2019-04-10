from typing import Dict, List
from abc import ABC, abstractmethod


__all__ = ['Elem', 'ElemList', 'ElemGroup', 'Model', 'Index']


class BaseElem(ABC):
    __slots__ = ('keys', '_transform')

    def __init__(self, *keys):
        self.keys = keys
        self._transform = None

    def __repr__(self):
        return f'{self.__class__.__name__}({" ".join(self.keys)})'

    def set_transform(self, t):
        """
        Callable that will transform input data after parsing. For example, to enforce a type.
        Set during model subclass load.
        """
        if t is not None:
            self._transform = t

    def do_transform(self, model: 'Model', data):
        """
        Transform input data (already parsed and filtered) into usable output.
        """
        if len(data) == 1:
            data = list(data.values())[0]

        if data is None:
            return

        if issubclass(self._transform, Model):
            return self._transform(model.client, data)
        elif isinstance(data, dict):
            return self._transform(**data)
        elif data is not None:
            return self._transform(data)

    @abstractmethod
    def parse(self, model: 'Model', data):
        """
        Parse data and return relevant data to be returned from the attribute.
        """


class Elem(BaseElem):
    """
    class _(Model):
        a: str = Elem('a')

    simple element.
    multiple keys can be specified to pass multiple data entries to the transform
    """
    __slots__ = ()  # make sure this doesn't get assigned a __dict__

    def parse(self, model: 'Model', data):
        return self.do_transform(model, {k: data.get(k, None) for k in self.keys})


class ElemList(BaseElem):
    """
    class _(Model):
        a: str = ElemList('a')

    Ensure that at least the first key given is a list in the data
    """
    __slots__ = ()  # make sure this doesn't get assigned a __dict__

    def parse(self, model: 'Model', data):
        return [
            self.do_transform(model, {
                key: data[key][i] if isinstance(data[key], list) else data[key]
                for key in self.keys
            })
            # since we requested the first key get us an iterable, we can base the length on this
            for i in range(len(data[self.keys[0]]))
        ]


class ElemGroup(BaseElem):
    """
    class _(Model):
        a: str = Elem('a*', 'b')[3]
        b: str = Elem('c*', 'b')[1:4]

    Groups up params following a pattern including a number and returns a list
    """
    __slots__ = ('range',)

    def __init__(self, *keys):
        super().__init__(*keys)
        self.range = None

    def __getitem__(self, item):
        self.range = item
        return self

    def parse(self, model: 'Model', data):
        if self.range is None:
            raise TypeError("No range provided in ElemGroup[...]")

        # convert __getitem__ input to a range to iterate over
        if isinstance(self.range, slice):
            r = range(self.range.start or 0, self.range.stop+1, self.range.step or 1)
        else:
            r = range(self.range+1)  # int input

        return [a for a in[
            # execute the Element transform over this key variation
            self.do_transform(model, {
                # generate this key variation and include it in the data
                # keys not containing * are passed untouched to each transform
                k.replace('*', ''): data[k.replace('*', str(i))]
                for k in self.keys
            })
            for i in r  # iterate over possible key variations
        ] if a is not None]



class Model:
    __slots__ = ('client', '_raw_data_',)  # in case subclasses want to use __slots__

    elems: Dict[str, BaseElem]
    __repr_attrs__: List[str] = ['id']

    def __init__(self, client, _dct=None, **kwargs):

        self.client = client

        # allow a dict to be passed in directly
        # allows Models to be set as Elem transforms easily
        if _dct is not None:
            kwargs.update(_dct)

        # store raw data as a pass-through for backwards-compatibility
        self._raw_data_ = kwargs

    @classmethod
    def __init_subclass__(cls):
        """called when anything subclasses Model, lets us process the attributes"""
        super().__init_subclass__()
        # filter to only Elems
        cls.elems = {}
        for k, e in cls.__dict__.items():
            if isinstance(e, BaseElem):
                e.set_transform(cls.__annotations__.get(k, None))
                cls.elems[k] = e

    def __getattribute__(self, item):
        if item in super(Model, self).__getattribute__('elems'):
            try:
                return self.elems[item].parse(self, self._raw_data_)
            except KeyError:
                raise AttributeError(item)
        else:
            return super(Model, self).__getattribute__(item)

    def __repr__(self):
        # TODO: sloppy and doesn't work well
        repr_attrs = [
            f'{e}:{getattr(self, e)}'
            for e in self.__repr_attrs__
            if getattr(self, e, None) is not None
        ]
        return f"{self.__class__.__name__}({' '.join(repr_attrs)})"

    def __getitem__(self, key):
        """
        For backwards compatibility, this class can be used like a dict.
        This will function as a simple pass-through to the stored raw data.
        """
        return self._raw_data_[key]

    @classmethod
    def columns(cls):
        s = set()
        for e in cls.elems.values():
            s.update(e.keys)

        return list(s)


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
