import typing as t

T = t.TypeVar("T", bound="Singleton")


class Singleton(object):
    def __new__(cls: t.Type[T], *args: t.Any, **kargs: t.Any) -> t.Any:
        if not hasattr(cls, "_instance"):
            cls._instance = super(Singleton, cls).__new__(cls)
            cls._instance.setup()
        return cls._instance
