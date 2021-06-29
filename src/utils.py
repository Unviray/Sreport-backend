from functools import wraps, lru_cache


CACHED_LIST = []


class Cache:
    """
    Like LRU_Cache but can be updated
    """

    def __init__(self, deps:list):
        self.deps = deps
        CACHED_LIST.append(self)

    def __call__(self, func):
        """
        This is the real decorator
        """

        @wraps(func)
        @lru_cache()
        def wrapped(*args, **kwargs):
            return func(*args, **kwargs)

        wrapped.cache = self

        self.func = wrapped
        return self.func

    def update(self):
        self.func.cache_clear()


def update_cache(deps):
    def _in(to_check, in_me):
        for _ in in_me:
            if (to_check == _) or isinstance(to_check, _):
                return True
        return False

    if isinstance(deps, list):
        for dep in deps:
            for cached in CACHED_LIST:
                if _in(dep, cached.deps):
                    cached.update()

    else:
        for cached in CACHED_LIST:
            if _in(deps, cached.deps):
                cached.update()
