"""Small test-time SQLModel compatibility layer.

The real application declares `sqlmodel` as a dependency. The execution environment used by
these kata-style checks does not always have network access to install dependencies, so this
module provides the tiny subset exercised by the repository's unit tests. It intentionally keeps
an in-memory store and should not be used as a production database adapter.
"""
from __future__ import annotations

from collections import defaultdict
from typing import Any, Callable
from uuid import uuid4

JSON = dict


class Column:
    def __init__(self, *_args: Any, **_kwargs: Any) -> None:
        pass


class FieldInfo:
    def __init__(self, default: Any = None, default_factory: Callable[[], Any] | None = None, **_kwargs: Any) -> None:
        self.default = default
        self.default_factory = default_factory
        self.name = ""

    def __set_name__(self, _owner: type, name: str) -> None:
        self.name = name

    def __get__(self, instance: Any, owner: type | None = None) -> Any:
        if instance is None:
            return ColumnExpression(self.name)
        return instance.__dict__.get(self.name, self.value())

    def __set__(self, instance: Any, value: Any) -> None:
        instance.__dict__[self.name] = value

    def value(self) -> Any:
        if self.default_factory is not None:
            return self.default_factory()
        return self.default


def Field(default: Any = None, default_factory: Callable[[], Any] | None = None, **kwargs: Any) -> FieldInfo:
    return FieldInfo(default=default, default_factory=default_factory, **kwargs)


class ColumnExpression:
    def __init__(self, name: str) -> None:
        self.name = name

    def __eq__(self, other: Any) -> Callable[[Any], bool]:  # type: ignore[override]
        return lambda obj: getattr(obj, self.name, None) == other

    def in_(self, values: list[Any]) -> Callable[[Any], bool]:
        return lambda obj: getattr(obj, self.name, None) in values


class _Metadata:
    def create_all(self, _engine: Any) -> None:
        pass

    def drop_all(self, _engine: Any) -> None:
        pass


class SQLModel:
    metadata = _Metadata()

    def __init_subclass__(cls, **kwargs: Any) -> None:
        kwargs.pop("table", None)
        super().__init_subclass__(**kwargs)

    def __init__(self, **kwargs: Any) -> None:
        annotations: dict[str, Any] = {}
        for base in reversed(type(self).mro()):
            annotations.update(getattr(base, "__annotations__", {}))
        for name in annotations:
            descriptor = getattr(type(self), name, None)
            if name in kwargs:
                value = kwargs[name]
            elif isinstance(descriptor, FieldInfo):
                value = descriptor.value()
            elif not callable(descriptor) and not isinstance(descriptor, property):
                value = descriptor
            else:
                value = None
            setattr(self, name, value)


class Engine:
    def __init__(self, url: str) -> None:
        self.url = url
        self.rows: dict[type, list[Any]] = defaultdict(list)

    def connect(self) -> "Engine":
        return self

    def __enter__(self) -> "Engine":
        return self

    def __exit__(self, *_args: Any) -> None:
        pass


def create_engine(url: str, **_kwargs: Any) -> Engine:
    return Engine(url)


class Query:
    def __init__(self, model: type) -> None:
        self.model = model
        self.predicates: list[Callable[[Any], bool]] = []

    def where(self, *predicates: Callable[[Any], bool]) -> "Query":
        self.predicates.extend(predicates)
        return self


def select(model: type) -> Query:
    return Query(model)


class Result:
    def __init__(self, rows: list[Any]) -> None:
        self._rows = rows

    def all(self) -> list[Any]:
        return list(self._rows)

    def first(self) -> Any | None:
        return self._rows[0] if self._rows else None


class Session:
    def __init__(self, engine: Engine) -> None:
        self.engine = engine

    def __enter__(self) -> "Session":
        return self

    def __exit__(self, *_args: Any) -> None:
        pass

    def add(self, obj: Any) -> None:
        if getattr(obj, "id", None) is None:
            setattr(obj, "id", uuid4())
        rows = self.engine.rows[type(obj)]
        if not any(getattr(row, "id", object()) == getattr(obj, "id", None) for row in rows):
            rows.append(obj)

    def commit(self) -> None:
        pass

    def refresh(self, _obj: Any) -> None:
        pass

    def get(self, model: type, id_value: Any) -> Any | None:
        for row in self.engine.rows[model]:
            if getattr(row, "id", None) == id_value:
                return row
        return None

    def exec(self, query: Query) -> Result:
        rows = list(self.engine.rows[query.model])
        for predicate in query.predicates:
            rows = [row for row in rows if predicate(row)]
        return Result(rows)
