# -*- coding: utf-8 -*-
# @Time    : 2024/12/6 21:35
# @Author  : AI悦创
# @FileName: generate.py
# @Software: PyCharm
# @Blog    ：https://bornforthis.cn/
# code is far away from bugs with the god animal protecting
#    I love animals. They taste delicious.
import os

base_root = '/Users/huangjiabao/GitHub/Github_Repo/vote_app/'



def generate_text(paths):
    text = ''
    for path in paths:
        filename = path.split('/')[-1]
        with open(base_root + path, 'r') as f:
            content = f.read()
            text += filename + ':\n' + content + '\n'
    with open('text.txt', 'w') as f:
        f.write(text)

lst = [
    'static/style.css',
    'templates/admin.html',
    'templates/index.html',
    'templates/category.html',
    'templates/group.html',
    'templates/results.html',
    'app.py',
]

if __name__ == '__main__':
    generate_text(lst)