import asyncio
import inspect
import threading

from typing_extensions import Callable


def synchronized_call(func: Callable, *args, **kwargs):
    if inspect.iscoroutinefunction(func):
        __res = None

        def __func(loop: asyncio.AbstractEventLoop):
            nonlocal __res, args, kwargs
            try:
                __res = loop.run_until_complete(func(*args, **kwargs))
            finally:
                loop.close()

        __thread = threading.Thread(
            target=__func,
            args=(asyncio.new_event_loop(),)
        )
        __thread.start()
        __thread.join(timeout=None)
        return __res
    return func(*args, **kwargs)


def sync_call(func: Callable):
    def wrapper(*args, **kwargs):
        return synchronized_call(func, *args, **kwargs)
    return wrapper
