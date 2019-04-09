from typing import Dict

__all__ = ['Elem', 'Model']


class Elem:
    __slots__ = ('key', 'transform')

    def __init__(self, key=None):
        self.key = key  # key to read from raw data
        self.transform = lambda _: _  # default is a pass-through

    def __repr__(self):
        return f'Elem({self.key})'


class Model:
    attrs: Dict[str, Elem]

    def __init__(self, client, _dct=None, **kwargs):

        self.client = client

        # allow a dict to be passed in directly
        # allows Models to be set as Elem transforms easily
        if _dct is not None:
            kwargs.update(_dct)

        # store raw data as a pass-through for backwards-compatibility
        self._raw_data_ = kwargs

        # go through all Elems this subclass stored when it was processed
        for name, elem in self.attrs.items():
            if elem.key in kwargs:
                data = kwargs.get(elem.key)
                if data is not None:
                    transform = elem.transform
                    if isinstance(elem.transform, list):
                        transform = transform[0]
                        if issubclass(transform, Model):
                            a = [transform(self.client, d) for d in data]
                        else:
                            a = [transform(d) for d in data]
                    else:
                        if issubclass(transform, Model):
                            a = transform(self.client, data)
                        else:
                            a = transform(data)
                    setattr(self, name, a)  # if the key exists, set the transformed data
            else:
                setattr(self, name, None)

    @classmethod
    def __init_subclass__(cls):
        """called when anything subclasses Model, lets us process the attributes"""
        super().__init_subclass__()
        # filter to only Elems
        cls.attrs = {}
        for k, e in cls.__dict__.items():
            if isinstance(e, Elem):
                a = cls.__annotations__.get(k, None)
                if a is not None:
                    e.transform = a
                cls.attrs[k] = e

    def __repr__(self):
        repr_attrs = [
            f'{e}:{getattr(self, e)}'
            for e in self.attrs
            if getattr(self, e) is not None
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
        return [e.key for e in cls.attrs.values()]
