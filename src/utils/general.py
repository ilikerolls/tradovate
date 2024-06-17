import contextlib
import threading
from datetime import datetime, date
from threading import Lock
import re


class Singleton(type):
    """
    Create a thread safe Singleton Class. Just add metaclass=metaclass=Singleton to your Class
    ex:

    from lib import Singleton
    class KlineHistory(metaclass=Singleton):
        def __init__(self):
            print("I am not a Singleton Class & will give the same instance even when called from Threads")
    """
    _instances = {}
    __singleton_lock = Lock()

    def __call__(cls, *args, **kwargs):
        # Check again for instance just in case another thread beat us to it
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton,
                                        cls).__call__(*args, **kwargs)
        return cls._instances[cls]


def create_a_thread(func, name: str = None, daemon: bool = True, **kwargs) -> threading.Thread:
    """
    Create & Start a thread, then return it's handle
    :param func: Function/method to run in the thread
    :param name: Optional: Name of Thread
    :param daemon: Optional: True(Deafault) = Thread is automatically killed when main program Exits, False = Must keep
    track of thread & stop manually via thread.stop()
    :param kwargs: Any additional arguments to be passed to threading.Thread()
    :return: Thread Handle
    """
    thread = threading.Thread(
        target=func, name=name, daemon=daemon, kwargs=kwargs
    )
    thread.start()
    return thread


def csv_to_list(string: str, cast_to=str) -> list:
    """
    Convert Comma Separated list into a List
    :param string: Comma Separated String to be converted into a list
    :param cast_to: What should each item in list be Cast to? Ex: 'str', 'int', 'float'
    :return: A list from csv string or an empty list if string is empty
    """
    return list(map(cast_to, string.replace(' ', '').split(','))) if string != "" else []


def parse_a_date(text: str) -> datetime:
    """
    Parse Date to a specific
    :param text:
    :return:
    """
    for fmt in ('%Y-%m-%dT%H:%M:%SZ', '%Y-%m-%dT%H:%M:%S.%f%z', '%Y-%m-%dT%H:%M:%S%z'):
        with contextlib.suppress(ValueError):
            return datetime.strptime(text, fmt)
    raise ValueError('no valid date format found')


def snake_case(text: str) -> str:
    """
    Return a class name in snake case form & removing _. For example: print_action will return PrintAction
    :param text: String to convert
    :return: Snake Case Class String ex: TradovateAction
    """
    return re.sub(r'_', '', text.title())


def string_to_date(dated_str: str) -> str:
    d = date.today()
    return str(d.strftime(dated_str).upper())