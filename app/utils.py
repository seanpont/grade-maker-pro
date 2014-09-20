# -*- coding: utf-8 -*-


def atterize(widget):
    if isinstance(widget, list):
        return [atterize(item) for item in widget]
    elif isinstance(widget, dict):
        for key in widget:
            widget[key] = atterize(widget[key])
        return AttrDict(widget)
    else:
        return widget


class AttrDict(dict):
    def __getattribute__(self, name):
        try:
            return super(AttrDict, self).__getattribute__(name)
        except AttributeError:
            return self.get(name)


# ===== LIST UTILS ===============================================================

def find(iterable, func):
    for i in iterable:
        if func(i):
            return i


def find_and_remove(iterable, func):
    iterable.remove(find(iterable, func))


# ===== TESTS ===============================================================


if __name__ == '__main__':
    d = {'a': 1, 'b': {'c': 3, 'd': 4}, 'e': [5, 6, 7], 'f': [{'g': 8}, {'h': 9}]}
    ad = atterize(d)
    print ad.a
    print ad.b
    print ad.b.c
    print ad.e[1]
    print ad.f[0].g
