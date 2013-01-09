# -*- coding: utf-8 -*-
import codecs
from lxml import etree
from lxml.etree import parse
from rus_corpora_parser import process_ruscorpora_file


if __name__ == "__main__":
    process_ruscorpora_file('/home/egor/rnc.xml','/home/egor/rnc_mystem.txt')