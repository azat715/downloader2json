import functools
import time


class Timer:
    def __init__(self) -> None:
        self.t_start = time.monotonic()

    def stop(self) -> float:
        return time.monotonic() - self.t_start

    @classmethod
    def start(cls) -> "Timer":
        return cls()


def logger_wraps(logger):
    def wrapper(func):
        @functools.wraps(func)
        def wrapped(*args, **kwargs):
            logger.opt(depth=1)
            logger.debug(f"Загрузка url {args[1]} началась")
            t = Timer.start()
            result = func(*args, **kwargs)
            time_delta = t.stop()
            logger.debug(f"Загрузка url {args[1]} закончилась за {time_delta}")
            return result

        return wrapped

    return wrapper


def async_logger_wraps(logger):
    def wrapper(func):
        @functools.wraps(func)
        async def wrapped(*args, **kwargs):
            logger.opt(depth=1)
            logger.debug(f"Загрузка url {args[1]} началась")
            t = Timer.start()
            result = func(*args, **kwargs)
            time_delta = t.stop()
            logger.debug(f"Загрузка url {args[1]} закончилась за {time_delta}")
            return await result

        return wrapped

    return wrapper
