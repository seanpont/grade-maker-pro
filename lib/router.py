import re

# list of route-handler tuples
ROUTES = []

# map of handler name : route.
# Each entry contains the class name in CamelCase and snake_case.
ROUTE_MAP = {}


def collect(file_name):
    __import__(file_name)
    return ROUTES


def route(path):
    """Use to annotate handlers. eg @route('/path')"""
    def wrap(handler):
        ROUTES.append((path, handler))
        ROUTE_MAP[handler.__name__] = path
        ROUTE_MAP[_camel_to_snake(handler.__name__)] = path
        return handler
    return wrap


def url_for(handler_name, *args):
    url = ROUTE_MAP[handler_name]
    for arg in args:
        url = re.sub('\(.+\)', str(arg), url, count=1)
    return url


def _camel_to_snake(name):
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()