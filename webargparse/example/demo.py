#!/usr/bin/env python3
'''
Author: penfree
Date: 2022-01-21 19:37:03

'''

from argparse import ArgumentParser
import webargparse.types as types
from datetime import date
import argparse
import json
import time

def getParser():
    # prog: 的内容是页面左侧"功能清单选择"下拉框中显示的内容
    # description: 功能说明, 可以写markdown, 会出现右侧顶部
    parser = ArgumentParser(prog='这是一个demo', description='''
    **这里可以写markdown**
    ''')

    # 选项的help是输入框的label
    parser.add_argument('-i', '--output', help='输入字符串')
    # int和float类型的输入框只能是数字
    parser.add_argument('--integer', dest='integer', help='这是一个数字', type=int)
    parser.add_argument('-s', dest='source', help='这是一个可以输入多值的字符串', nargs='*', default=['a', 'b'])
    # 这是一个单选的下拉列表
    parser.add_argument('--output-type', dest='output_type', help='选择返回结果类型, 测试工具输出结果样式',
                        choices=['文件', '表格', '短字符串', 'bytes', '字典', '短字符串', '长字符串', 'markdown', '折线图'], default='表格')
    # 这是一个多选框
    parser.add_argument('--multi', dest='multi', help='多选框, 可以选择多个选项', nargs='+' , default=['表格', '文件'],
                        choices=['文件', '表格', '短字符串', 'bytes', '字典', '短字符串', '长字符串', 'markdown', '折线图'])
    # 这是一个必选的字符串, 如果不填会报错
    parser.add_argument('-r', dest='required_str', help='这是一个必选的字符串, 不填会报错', required=True)
    # 上传文件, 上传后的文件会打开并将文件对象传递给 args.file
    parser.add_argument('-f', dest='file', help='上传一个文件, 输出文件前10行', type=argparse.FileType(mode='r', encoding='utf-8'))
    parser.add_argument('--store', action='store_true', dest='store_true', help='单选框')
    parser.add_argument('--date', type=date.fromisoformat, help='选择日期')
    parser.add_argument('--time', type=types.time, help='选择时间, 目前只能分别得到时间后拼接在一起')
    return parser

def STREAMLIT_DETAIL_FUNCTION(rows):
    return f'''
* 详细结果
```
{json.dumps(rows, ensure_ascii=False)}
```
'''

def process(args):
    if args.file:
        count = 0
        with args.file:
            for line in args.file:
                print(line)
                count += 1
                if count >= 10:
                    break
    time.sleep(3)
    print(args)
    #return [{'a':1, 'b':3, 'c': 4}, {'a':1, 'b':3, 'd': 4},]
    #return [1,2,3,4]
    if args.output_type == '文件':
        from io import StringIO
        return StringIO('这是一个测试文件')
    elif args.output_type == '表格':
        return [{'a':1, 'b':3, 'c': 4}] * 200
    elif args.output_type == '短字符串':
        return '短字符串'
    elif args.output_type == '折线图':
        return ([{'a':1, 'b':3, 'c': 4}] * 200, 'line_chart')
    elif args.output_type == '长字符串':
        return ''.join(['长字符串'] * 500)
    elif args.output_type == 'markdown':
        return '''<markdown># 一级标题
## 二级标题
</markdown>'''
    elif args.output_type == 'bytes':
        return b'this is a bytes'

    return {'a':1, 'b':3, 'c': 4}

# ArgumentParser对象, 必须有此变量
STREAMLIT_PARSER = getParser()
# 处理参数的函数, 必须有此变量
STREAMLIT_FUNCTION = process

if __name__ == '__main__':
    args = getParser().parse_args()
    process(args)

