#!/usr/bin/env python3
'''
Author: penfree
Date: 2022-01-21 17:12:37

'''

import argparse
from copy import deepcopy
from typing import List
import streamlit as st
from webargparse.pages.argparsepage import ArgparsePage
from argparse import ArgumentParser


class Homepage:

    def __init__(self):
        self.pages: List[ArgparsePage] = []
        #self.pages = []

    def addPage(self, page: ArgparsePage):
        #
        # #   'title': page.title,
        #    'page': page
        #})
        self.pages.append(page)

    def render(self):
        # Drodown to select the page to run
        page = st.sidebar.selectbox(
            '功能清单,请选择',
            self.pages,
            format_func=lambda p: p.title
        )

        page.render()

    @classmethod
    def getSubParsers(cls, parser: ArgumentParser):
        sub_parsers = [action for action in parser._actions if isinstance(action, argparse._SubParsersAction)]
        # 没有subparser, 直接返回
        if not sub_parsers:
            return [parser]
        elif len(sub_parsers) > 1:
            st.error('一个parser中最多只能有一个subparsers')
            return []
        result = []
        sub_action = sub_parsers[0]
        for name, p in sub_action.choices.items():
            t: ArgumentParser = deepcopy(p)
            if parser.description:
                t.description = parser.description + (t.description or '')
            t.add_argument(dest=sub_action.dest, const=name, action='store_const', help='子命令action不可更改')
            for action in parser._actions:
                if isinstance(action, (argparse._HelpAction, argparse._SubParsersAction)):
                    continue
                t._add_action(deepcopy(action))
            result.append(t)
        return result

    @classmethod
    def run(cls):
        import sys, os, pkgutil, importlib
        st.set_page_config(layout="wide")
        hp = Homepage()
        module_name = os.environ['WEB_ARGPARSE_MODULE_NAME']
        modules = []
        for m in module_name.split(','):
            module = importlib.import_module(m)
            modules.append(module)
        while modules:
            m = modules.pop(0)
            if hasattr(m, 'STREAMLIT_FUNCTION') and hasattr(m, 'STREAMLIT_PARSER'):
                parser = getattr(m, 'STREAMLIT_PARSER')
                detail_func = None
                if hasattr(m, 'STREAMLIT_DETAIL_FUNCTION'):
                    detail_func = getattr(m, 'STREAMLIT_DETAIL_FUNCTION')
                for sparser in cls.getSubParsers(parser):
                    p = ArgparsePage(parser=sparser,
                                 func=getattr(m, 'STREAMLIT_FUNCTION'),
                                 detail_func=detail_func)
                    hp.addPage(p)
            if hasattr(m, '__path__'):
                for sm in pkgutil.iter_modules(m.__path__):
                    child = importlib.import_module(f'{m.__name__}.{sm.name}')
                    modules.append(child)
        hp.render()


if __name__ == '__main__':
    from webargparse.example.demo import STREAMLIT_FUNCTION, STREAMLIT_PARSER
    p = ArgparsePage(parser=STREAMLIT_PARSER, func=STREAMLIT_FUNCTION)
    hp = Homepage()
    hp.addPage(p)
    hp.render()
