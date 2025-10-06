from importlib.metadata import version as get_version


def get_biomechzoo_version() -> str:
    return get_version("biomechzoo")
