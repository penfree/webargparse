#!/usr/bin/env python3
'''
Author: penfree
Date: 2022-01-21 19:37:03

'''

from argparse import ArgumentParser
import argparse
import webargparse.types as types
import streamlit as st

def getParser():
    parser = ArgumentParser(prog='包含子命令的demo', description='这个demo中包含多个子命令')
    parser.add_argument('-i', '--output', help='输入字符串')
    parser.add_argument('--choice', dest='choices', choices=['选项1', '选项2', '选项3'])
    sub_parsers = parser.add_subparsers(dest='action')
    name_parser = sub_parsers.add_parser('file', help='子命令1')
    name_parser.add_argument('--test', action='store_true', help='单选框')
    name1_parser = sub_parsers.add_parser('mq', help='子命令2')
    name1_parser.add_argument('--url', default='default url', required=True, help='输入url')
    return parser

STREAMLIT_PARSER = getParser()

def process(args):
    #print(args)
    # 在这个函数里面, 你实际上可以随意的使用streamlit的API来绘制组件, 但如果你这么做了, 他就没办法在本地执行了
    st.write(args)
    #return [{'a':1, 'b':3, 'c': 4}, {'a':1, 'b':3, 'd': 4},]
    #return [1,2,3,4]

STREAMLIT_FUNCTION = process

if __name__ == '__main__':
    args = getParser().parse_args()
    process(args)

