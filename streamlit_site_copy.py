import streamlit as st
from graphs import *
from streamlit.components.v1 import html
import vl_convert as vlc

st.set_page_config(layout="wide")
st.title("Traffic Accident Analysis in New York City")



def render_svg(svg, width="60%", height="auto"): 
    """Renders the given svg string with specified width and height."""
    b64 = base64.b64encode(svg.encode("utf-8")).decode("utf-8")
    html = f'<img src="data:image/svg+xml;base64,{b64}" style="width: {width}; height: {height};"/>'
    st.write(html, unsafe_allow_html=True, use_container_width=True)

colors = {"bg": "#eff0f3", "col1": "#4f8c9d", "col2": "#6ceac0"}


accident_data = get_accident_data("dataset_v1.csv", sample=True)
weather_data = get_weather_data(accident_data) 

##############################################

# mapa = get_map()
# ny_df, bur = get_buroughs(mapa)

# hex_data = calculate_spatial_data(accident_data, mapa)
# map_chart, bar_chart=plot_map(hex_data,mapa,ny_df,bur)
# map_chart.save('resources/testmap.svg')

# print("Mapa guardado")
##############################################



chart_1 = get_chart_1(accident_data, w=150, h=390)
chart_2 = create_chart2(q2_preprocessing(accident_data), width=1000, height=350)
data_3 = q3_preprocessing(accident_data)
chart_3 = create_chart3(data_3, color_palette=get_palette(), width=700, height=180)
# open resources/map.svg
with open("resources/map2.svg", "r") as f:
    map_svg = f.read() 

# mapa = get_map()
# ny_df, bur = get_buroughs(mapa)

# hex_data = calculate_spatial_data(accident_data, mapa)
# map_chart, chart_map_bars=plot_map(hex_data,mapa,ny_df,bur)
  

#chart_map_bars = borough_chart(accident_data, w=500, h=350)
    
chart_5 = weather_chart(weather_data, h=350, w=525) 





with st.container():
    col1, col2 = st.columns([0.6, 0.4])
    with col1:
        st.markdown("### Where do accidents happen?")
        render_svg(map_svg)
        
    with col2:
        st.markdown("### Accidents by borough")
       # st.altair_chart(chart_map_bars, use_container_width=True)

    
  
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
