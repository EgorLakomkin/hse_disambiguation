# -*- coding: utf-8 -*-
__author__ = 'egor'

from pymorphy import get_morph

PYMORPHY_PATH = '/home/egor/pymorphy_dict'

morph = get_morph(PYMORPHY_PATH)

def get_morph_info(word):
    return morph.get_graminfo( word.upper() )


if __name__ == "__main__":
    print get_morph_info(u"тест")