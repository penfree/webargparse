#!/usr/bin/env python3
'''
Author: penfree
Date: 2022-01-21 17:16:37

'''
from argparse import _StoreTrueAction, Action, ArgumentParser, Namespace, SUPPRESS
import argparse
from typing import Any, Callable, List, Tuple
import streamlit as st
from contextlib import redirect_stdout, redirect_stderr
import io
import pandas as pd
from tempfile import NamedTemporaryFile
import webargparse.types as types
from datetime import datetime, date
from st_aggrid import AgGrid, GridUpdateMode
from st_aggrid.grid_options_builder import GridOptionsBuilder

from streamlit.state.widgets import NoValue

@st.cache
def dftocsv(df):
    if isinstance(df, list):
        df = pd.DataFrame(df)
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv().encode('utf-8')

class StreamlitPage:

    def __init__(self, title: str):
        # 页面标题
        self.title = title

    def render(self):
        """渲染页面
        """
        raise NotImplementedError()

    def __str__(self):
        return self.title

    def __eq__(self, __o: object) -> bool:
        return str(__o) == str(self)


class ActionWebComponent:

    def __init__(self, action: Action):
        self.action = action

    @property
    def Label(self):
        text = ' '.join(self.action.option_strings)
        if not text:
            text = self.action.dest
        if self.action.help:
            text = f'{self.action.help}({text})'
        if self.action.required or self.action.nargs in ('+', ):
            text += '[必须]'
        return text

    @property
    def Default(self):
        # 允许多值的字符串类型
        if isinstance(self.action.default, list) and not self.action.choices:
            return '\n'.join(self.action.default)
        return self.action.default or ''

    @property
    def PlaceHolder(self):
        if self.action.nargs in ('+', '*'):
            return '支持多值, 每个参数一行'
        else:
            return ''


    def render(self):
        # 带选项
        if self.action.choices:
            # 多选
            if self.action.nargs in ('*', '+'):
                return st.multiselect(label=self.Label, options=list(self.action.choices), default=self.Default)
            # 单选
            else:
                return st.selectbox(label=self.Label,
                                    options=list(self.action.choices),
                                    index= 0 if self.Default not in self.action.choices else list(self.action.choices).index(self.Default))
        # store_true
        elif isinstance(self.action, _StoreTrueAction):
            return st.checkbox(label=self.Label)
        elif isinstance(self.action, argparse._StoreConstAction):
            return st.text_input(label=self.Label, value=self.action.const, disabled=True)
        elif isinstance(self.action.type, argparse.FileType) or self.action.type == open:
            return st.file_uploader(self.Label)
        elif self.action.type == types.date or self.action.type == types.datetime or self.action.type == date.fromisoformat:
            return st.date_input(self.Label)
        elif self.action.type == types.time:
            return st.time_input(self.Label)
        else:
            # 数字
            if self.action.type is int or self.action.type is float:
                default = self.Default or None
                if default is None:
                    default = 0 if self.action.type is int else 0.0
                return st.number_input(label=self.Label, value=default if default is not None else NoValue())
            else:
                if self.action.nargs in ('*', '+'):
                    return st.text_area(label=self.Label, value=self.Default, placeholder=self.PlaceHolder)
                else:
                    return st.text_input(label=self.Label, value=self.Default, placeholder=self.PlaceHolder)

    @property
    def Required(self):
        return self.action.required or self.action.nargs == '+'

    def parseResult(self, result):
        """解析组件的返回值, 并转换成action中预期的类型
        """
        if not result and self.Required:
            raise ValueError('缺少必填项: %s' % self.Label)
        if self.action.type == open or isinstance(self.action.type, argparse.FileType):
            # 文件类型
            if result is not None:
                if isinstance(self.action.type, argparse.FileType) and 'b' in self.action.type._mode:
                    tf = NamedTemporaryFile(mode='wb+')
                    tf.write(result.getvalue())
                else:
                    tf = NamedTemporaryFile(mode='w+')
                    tf.write(result.getvalue().decode('utf-8'))
                tf.seek(0)
                return tf
        elif self.action.type == types.datetime:
            return datetime(result.year, result.month, result.day, 0, 0, 0)
        elif self.action.type == types.date or self.action.type == types.time or self.action.type == date.fromisoformat:
            return result
        elif not isinstance(result, str):
            return result
        else:
            type_func = self.action.type or str
            value = type_func(result)
            if isinstance(value, str):
                value = value.strip()
                if self.action.nargs in ('*', '+'):
                    if not value:
                        return []
                    else:
                        return value.split('\n')  # 4个空格
            return value

class ArgparsePage(StreamlitPage):

    def __init__(self, parser: ArgumentParser, func: Callable, title=None, detail_func=None):
        """

        Args:
            parser (ArgumentParser): 工具对应的参数选项
            func (Callable): 处理命令行参数的函数
            title (str, optional): 工具标题, 默认取parser.prog. Defaults to None.
        """
        super().__init__(title or parser.prog or parser.description or '-')
        self.parser = parser
        self.func = func
        self.detail_func = detail_func

    def getComponents(self):
        return [
            ActionWebComponent(action) for action in self.parser._actions if action.default != SUPPRESS
        ]

    def getArgs(self, form_result: List[Tuple[ActionWebComponent, Any]]) -> Namespace:
        """将form返回的结果转换成argparse的解析结果

        Args:
            form_result (List[ActionWebComponent, Any]): form中返回的对应于每个action的取值

        Returns:
            Namespace: 一个namespace, 与argparse在命令行返回的一样
        """
        args = Namespace()
        for component, value in form_result:
            setattr(args, component.action.dest, component.parseResult(value))
        return args

    def renderResult(self, ret_value):
        """渲染处理函数的返回结果
        """
        if not ret_value:
            return
        # list和DataFrame展示结果, 最多显示100行,防止出错
        if isinstance(ret_value, (pd.DataFrame, list)):
            if isinstance(ret_value, list):
                ret_value = pd.DataFrame(ret_value)
            csv = dftocsv(ret_value)
            st.caption('共 %s 条记录' % len(ret_value.index))
            gb = GridOptionsBuilder.from_dataframe(ret_value)
            gb.configure_pagination()
            gb.configure_selection('single')
            gridOptions = gb.build()
            update_mode = GridUpdateMode.VALUE_CHANGED
            if self.detail_func:
                update_mode = GridUpdateMode.MODEL_CHANGED
            result = AgGrid(ret_value, gridOptions=gridOptions,update_mode=GridUpdateMode.MODEL_CHANGED)
            st.download_button(label='下载csv', data=csv, help='点击将数据以csv文件下载')
            if result['selected_rows']:
                st.caption('详细信息:')
                st.write(self.detail_func(result['selected_rows']))
        # dict展示json
        elif isinstance(ret_value, dict):
            st.caption('执行结果:')
            st.json(ret_value)
        # bytes下载二进制文件
        elif isinstance(ret_value, bytes):
            st.caption('文件已生成, 请点击下载:')
            st.download_button(label='下载文件', data=ret_value)
        # 如果是文件对象, 下载文件
        elif hasattr(ret_value, 'read'):
            st.caption('文件已生成, 请点击下载:')
            data = ret_value.read()
            ret_value.close()
            st.download_button(label='下载文件', data=data)
        # str 如果很短就直接展示, 太长则下载文件
        elif isinstance(ret_value, str):
            # 用<markdown></markdown>包围的字符串渲染成markdown
            if ret_value.startswith('<markdown>') and ret_value.endswith('</markdown>'):
                st.markdown(ret_value[10:-11])
            elif len(ret_value) < 1024:
                st.caption('执行结果:')
                st.write(ret_value)
            else:
                st.download_button(label='下载文件', data=ret_value, help='生成数据过大, 点击下载文件')
        elif isinstance(ret_value, types.ResultData):
            ret_value.render()
        elif isinstance(ret_value, tuple):
            t = types.ResultData(ret_value[0], type=ret_value[1])
            t.render()

    def render(self):
        """渲染页面
        """
        if self.parser.description:
            st.markdown(self.parser.description)
        components = self.getComponents()
        submited = None
        result = []
        if components:
            with st.sidebar.form(key='tool_form'):
                result: List[Tuple[ActionWebComponent, Any]] = []
                for component in components:
                    result.append((component, component.render()))
                submited = st.form_submit_button(label='提交')
                if submited:
                    st.session_state['submited'] = True

        if submited or not components or ('submited' in st.session_state and st.session_state['submited']):
            try:
                args = self.getArgs(result)
            except ValueError as e:
                st.error(str(e))
            else:
                f = io.StringIO()
                ret_value = None
                with redirect_stdout(f):
                    with redirect_stderr(f):
                        try:
                            with st.spinner('Loading...'):
                                ret_value = self.func(args)
                        except Exception as e:
                            print(e)
                if ret_value:
                    self.renderResult(ret_value)
                fvalue = f.getvalue()
                if fvalue:
                    st.markdown(f'''
    ### 输出:
    {f.getvalue()}
    ''')

