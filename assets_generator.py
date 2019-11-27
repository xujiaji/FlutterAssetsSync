#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
自动生成 flutter 项目assets资源配置
"""

__author__ = 'XuJiaji'

import os
import re
import subprocess
from functools import reduce

RE_ASSETS = re.compile(r'# assets-generator-begin[\s\S]+# assets-generator-end')
RE_2_3X = re.compile(r'(2.0x/)|(3.0x/)')

PATH = 'assets'

def start_server():
    print('Serving HTTP on http://127.0.0.1:3333')
    out_bytes = subprocess.check_output(['python3', '-m', 'http.server', '3333'])
    out_text = out_bytes.decode('utf-8')
    print(out_text)


def replace_content(content):
    with open('pubspec.yaml', 'r') as fr:
        result = re.sub(RE_ASSETS, content, fr.read())
        with open('pubspec.yaml', 'w') as fw:
            fw.write(result)


def find_assets(path, list):
    if os.path.isfile(path):
        return path
    assets = os.listdir(path)
    for f in assets:
        value = find_assets('%s/%s' % (path, f), list)
        if value:
            list.append(value)
    return None


def formatter(origin):
    src = origin.replace('2.0x/', '').replace('3.0x/', '')
    arr = re.split(r'[/_.]', src[:src.rindex('.')])
    res = ''
    for i in arr:
        if i is None or i == '':
            continue
        res = res + i[0].upper() + i[1:]
    res = res[0].lower() + res[1:]
    return [src, res, origin]


if __name__ == '__main__':
    find_list = []
    find_assets(PATH, find_list)
    no2x3x_list = []
    for l in list(find_list):
        if l.find('.DS_Store') > -1:
            find_list.remove(l)
            continue
        nox = l
        if l.find('2.0x/') > -1 or l.find('3.0x/') > -1:
            nox = re.sub(RE_2_3X, '', l)
            if nox in find_list:
                find_list.remove(nox)
        no2x3x_list.append(nox)
    yaml_content = '# assets-generator-begin\n    - %s\n  # assets-generator-end' % reduce(lambda x, y: x + '\n    - ' + y,  sorted(no2x3x_list, key=str.lower))
    replace_content(yaml_content)

    class_list = map(formatter, sorted(find_list, key=lambda s: re.sub(RE_2_3X, '', s.lower())))
    class_r = 'class R {\n%s}' % reduce(lambda x, y: x + y, map(lambda x: "  /// ![](http://127.0.0.1:3333/%s)\n  static final String %s = '%s';\n" % (x[2], x[1], x[0]), class_list))

    r = 'lib/r.dart'
    if os.path.exists(r):
        os.remove(r)
    with open(r, 'w') as fw:
        fw.write(class_r)
    start_server()