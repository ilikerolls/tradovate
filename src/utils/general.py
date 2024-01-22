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


def snake_case(text: str) -> str:
    return re.sub(r'_', '', text.title())


def csv_to_list(string: str, cast_to=str) -> list:
    """
    Convert Comma Separated list into a List
    :param string: Comma Separated String to be converted into a list
    :param cast_to: What should each item in list be Cast to? Ex: 'str', 'int', 'float'
    """
    return list(map(cast_to, string.replace(' ', '').split(',')))


if __name__ == "__main__":
    print(f"Snake case name of print_action = {snake_case(text='print_action')}")