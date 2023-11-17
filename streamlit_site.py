import streamlit as st
from graphs import *
from streamlit.components.v1 import html

colors = {"bg": "#eff0f3", "col1": "#4f8c9d", "col2": "#6ceac0"}


accident_data = get_accident_data("dataset_v1.csv", sample=True)
chart_1 = get_chart_1(accident_data)

st.altair_chart(chart_1)

st.image("resources/map.png")

chart_2 = create_chart2(q2_preprocessing(accident_data))

st.altair_chart(chart_2)
