import plotly.express as px
import streamlit as st

def render_charts(df):
    if 'total' in df.columns:
        fig = px.histogram(df, x='extraction_confidence')
        st.plotly_chart(fig)