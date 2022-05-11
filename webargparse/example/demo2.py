#!/usr/bin/env python3
'''
Author: penfree
Date: 2022-01-24 18:07:15

'''

from argparse import ArgumentParser
import streamlit as st
from st_aggrid import AgGrid
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode


STREAMLIT_PARSER = ArgumentParser(prog='自由模式测试')

def STREAMLIT_FUNCTION(args):
    df = pd.DataFrame({"col1": [1, 2, 3], "col2": [4, 5, 6]})

    options_builder = GridOptionsBuilder.from_dataframe(df)
    options_builder.configure_column('col1', editable=True)
    options_builder.configure_selection("single")
    grid_options = options_builder.build()

    grid_return = AgGrid(df, grid_options, update_mode=GridUpdateMode.MODEL_CHANGED)
    selected_rows = grid_return["selected_rows"]

    st.write(selected_rows)
