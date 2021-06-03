import argparse
from typing import List, Union


class ArgumentParser(argparse.ArgumentParser):
    """Literally just a class so that we can control the error that gets produced."""

    def error(self, message):
        raise RuntimeError(message)


def find_change(now: int, history: List[int]) -> Union[int, None]:
    """Function for figuring out 7 day change from rank history."""
    if now is None or history is None:
        return None
    index = 7
    if len(history) < 7:
        index = len(history)
    return history[-index] - now
