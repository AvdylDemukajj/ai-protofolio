import streamlit as st
import pandas as pd

def render_review_table(df):
    return st.dataframe(df, use_container_width=True)