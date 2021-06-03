import argparse
from typing import List, Union


class ArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        raise RuntimeError(message)


def find_change(now: int, history: List[int]) -> Union[int, None]:
    if now is None or history is None:
        return None
    index = 7
    if len(history) < 7:
        index = len(history)
    return history[-index] - now
