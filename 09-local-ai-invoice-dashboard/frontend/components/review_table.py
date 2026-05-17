import streamlit as st
import pandas as pd

def render_review_table(df):
    st.dataframe(df)