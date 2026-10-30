import copy
import json
import os
from threading import RLock
from typing import Any


class GBEncoder(json.JSONEncoder):
    def default(self, o):
        try:
            return super().default(o)
        except TypeError:
            # o est une classe, pas un objet
            if isinstance(o, type):
                # repr d'une classe de la forme <class 'foo'>
                # None va être interprété par GBDecoder
                return {'cls': repr(o).split("'")[1], 'kwargs': None}

            for fun in ['to_json', 'json']:
                if hasattr(o, fun):
                    f = getattr(o, fun)
                    if callable(f):
                        return f()
            return repr(o)


class GBDecoder(json.JSONDecoder):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.create_instance = True

    def decode(self, s, _w=...):
        if not isinstance(s, str):
            std = s
        else:
            try:
                std = super().decode(s)
            except:
                std = super().decode(f'"{s}"')

        if isinstance(std, (list, tuple)):
            return [self.decode(e) for e in std]

        elif isinstance(std, set):
            return {self.decode(e) for e in std}

        elif isinstance(std, dict):
            std = {self.decode(k): self.decode(v) for k, v in std.items()}
            if {'cls', 'kwargs'}.issubset(std.keys()):
                cls = self.instanciate(std['cls'].split('.'))
                kwargs = std['kwargs']
                if kwargs is None:
                    return cls
                return cls(**kwargs)

        elif isinstance(std, str):
            if std.lower() in ['oui', 'o', 'yes', 'y', 'vrai', 'v', 'true']:
                std = True
            elif std.lower() in ['non', 'n', 'no', 'faux', 'f', 'false']:
                std = False
            elif std.lower() in ['none', 'null']:
                std = None
            elif std.isdigit():
                std = int(std)
        return std

    @classmethod
    def instanciate(cls, path: list[str], _from=None):
        if not path:
            return _from
        if path[-1] in __builtins__:
            return __builtins__[path[-1]]
        if path[-1] in globals():
            return globals()[path[-1]]
        if path[-1] in locals():
            return locals()[path[-1]]
        if _from is None:
            _from = __import__(path[0])
            path = path[1:]
        return cls.instanciate(path[1:], getattr(_from, path[0]))


class JsonStore:
    JSON_FORMAT_READ = {'cls': GBDecoder}
    JSON_FORMAT_WRITE = {'cls': GBEncoder, 'indent': 2}

    def __init__(self, filename: str):
        self.filename = filename
        self._lock = RLock()
        self._data: dict[str, Any] = {}
        self._last_mtime: float = 0.0
        self._load()

    # --------- internals ---------

    def _load(self):
        try:
            mtime = os.path.getmtime(self.filename)
            if mtime == self._last_mtime:
                return

            with open(self.filename, "r") as f:
                self._data = json.load(f, **self.JSON_FORMAT_READ)

            self._last_mtime = mtime

        except (FileNotFoundError, json.JSONDecodeError):
            self._data = {}
            self._last_mtime = 0.0

    def _write(self):
        with open(self.filename, "w") as f:
            json.dump(self._data, f, **self.JSON_FORMAT_WRITE)
        self._last_mtime = os.path.getmtime(self.filename)

    # --------- public API ---------

    def data(self) -> dict:
        with self._lock:
            self._load()
            return self._data

    def save(self):
        with self._lock:
            self._write()

    def update(self, func):
        """Mutation directe + reload safe"""
        with self._lock:
            self._load()
            result = func(self._data)
            self._write()
            return result


class Transaction:
    def __init__(self, store: JsonStore):
        self.store = store
        self._backup = None

    def __enter__(self):
        self.store._lock.acquire()
        self.store._load()
        self._backup = copy.deepcopy(self.store._data)
        return self.store._data

    def __exit__(self, exc_type, exc, tb):
        if exc_type is not None:
            # rollback
            self.store._data = self._backup
        else:
            # commit
            self.store._write()

        self.store._lock.release()
        return False  # ne supprime pas les exceptions
