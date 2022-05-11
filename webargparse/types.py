#!/usr/bin/env python3
'''
Author: penfree
Date: 2022-01-22 02:21:27

'''

import arrow
import datetime as dt
import time as tm
import streamlit as st

def date(s) -> dt.date:
    return arrow.get(s).date

def datetime(s) -> dt.datetime:
    return arrow.get(s).naive

def time(s) -> dt.time:
    t = tm.strptime(s, '%H:%M:%S')
    return dt.time(t.tm_hour, t.tm_min, t.tm_sec)

class ResultData:

    RESULT_TYPE_SMALL_STRING = 'small_str'
    RESULT_TYPE_LONG_STRING = 'long_str'
    RESULT_TYPE_BYTES = 'long_str'
    RESULT_TYPE_FILE_OBJECT = 'file'
    RESULT_TYPE_DATAFRAME = 'dataframe'
    RESULT_TYPE_LIST = 'list'
    RESULT_TYPE_DICT = 'dict'
    RESULT_TYPE_LINE_CHART = 'line_chart'
    RESULT_TYPE_BAR_CHART = 'bar_chart'
    RESULT_TYPE_AREA_CHART = 'area_chart'
    RESULT_TYPE_MAP = 'map'
    RESULT_TYPE_IMAGE = 'image'

    def __init__(self, data, type="dataframe", **kwargs):
        self.data = data
        self.type = type
        self.kwargs = kwargs

    def render(self):
        if self.type == self.RESULT_TYPE_AREA_CHART:
            st.area_chart(self.data, **self.kwargs)
        elif self.type == self.RESULT_TYPE_BAR_CHART:
            st.bar_chart(self.data, **self.kwargs)
        elif self.type == self.RESULT_TYPE_LINE_CHART:
            st.line_chart(self.data, **self.kwargs)
        elif self.type == self.RESULT_TYPE_MAP:
            st.map(self.data, **self.kwargs)
        elif self.type == self.RESULT_TYPE_IMAGE:
            st.image(self.data)
        else:
            st.dataframe(self.data.header(100))
