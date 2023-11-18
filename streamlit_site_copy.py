import streamlit as st
from graphs import *
from streamlit.components.v1 import html

st.set_page_config(layout="wide")


# def render_svg(svg):
#     """Renders the given svg string."""
#     b64 = base64.b64encode(svg.encode("utf-8")).decode("utf-8")
#     html = r'<img src="data:image/svg+xml;base64,%s"/>' % b64
#     st.write(html, unsafe_allow_html=True, use_container_width=True)

def render_svg(svg, width="70%", height="auto"):
    """Renders the given svg string with specified width and height."""
    b64 = base64.b64encode(svg.encode("utf-8")).decode("utf-8")
    html = f'<img src="data:image/svg+xml;base64,{b64}" style="width: {width}; height: {height};"/>'
    st.write(html, unsafe_allow_html=True, use_container_width=True)

colors = {"bg": "#eff0f3", "col1": "#4f8c9d", "col2": "#6ceac0"}

st.title("Traffic Accident Analysis in New York City")

accident_data = get_accident_data("dataset_v1.csv", sample=True)
chart_1 = get_chart_1(accident_data, w=150, h=390)
chart_2 = create_chart2(q2_preprocessing(accident_data), width=1000, height=350)
data_3 = q3_preprocessing(accident_data)
chart_3 = create_chart3(data_3, color_palette=get_palette(), width=700, height=180)
# open resources/map.svg
with open("resources/map.svg", "r") as f:
    map_svg = f.read()
weather_data = get_weather_data(accident_data)
chart_5 = weather_chart(weather_data, h=350, w=525) 



with st.container():
    #col, _   = st.columns([0.8, 0.2])
    #with col:
        st.markdown("### Where do accidents happen?")
        render_svg(map_svg)


    
    
    # make the container into two columns
        #col1, col2 = st.columns([0.4, 0.6])
        # in column 1 plot chart 1 and chart 3
        # titles are: Before and After the Pandemic and Accidents by time of day
        #col1.markdown("### Vehicle type")
        #col1.altair_chart(chart_2, use_container_width=True)
        #col2.markdown("### Accidents by time of day")
        #col2.altair_chart(chart_3, use_container_width=True)
with st.container():
    col1, col2 = st.columns([0.4, 0.6])
    with col1:
        # before and after the pandemic
        st.markdown("### Percentage of accidents by vehicle type")
        st.altair_chart(chart_2, use_container_width=True)
    with col2:
        # weather
        st.markdown("### Weather")
        st.altair_chart(chart_5)



with st.container():
    col1, col2 = st.columns([0.5, 0.5])
    with col1:
        # accidents by time of day
        st.markdown("### Accidents by time of day")
        st.altair_chart(chart_3, use_container_width=True)
    with col2: 
        # before and after the pandemic
        st.markdown("### Before and After the Pandemic")
        st.altair_chart(chart_1)
    
# We get all charts
