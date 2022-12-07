import streamlit as st
import pandas as pd
import numpy as np
from streamlit_folium import folium_static
import folium
from folium.plugins import FastMarkerCluster, Fullscreen
from datetime import datetime
from plotly import graph_objs as go

st.set_page_config(
        page_title="GTC EXPLORER | KŁAPEYE FOUNDATION",
        page_icon="logo.png",
        layout="wide",
)
padding = 0
st.markdown(f""" <style>
    .reportview-container .main .block-container{{
        padding-top: {padding}rem;
        padding-right: {padding}rem;
        padding-left: {padding}rem;
        padding-bottom: {padding}rem;
    }} </style> """, unsafe_allow_html=True)

col1, col2 = st.sidebar.columns([40,60])
col1.image("logo.png",width=100)
st.image("dataset-cover.png", use_column_width=True)
col2.title("KŁAPEYE FOUNDATION")
col2.text("GTC Explorer v0.6")
col3, col4 = st.sidebar.columns(2)
data = pd.read_csv("klapeye-global-terrorism.csv")
data.replace(r'\s+', np.nan, regex=True)
data['DATE'] = pd.to_datetime(data['DATE']).dt.date
data['DEAD'] = data['DEAD'].astype('Int64')
data['INJURED'] = data['INJURED'].astype('Int64')
fromdate = col3.date_input(
    "FROM", value=(pd.Timestamp("2001-01-01").date()), min_value=(pd.Timestamp(min(data['DATE'])).date()), max_value=(pd.Timestamp(max(data['DATE'])).date()))
todate = col4.date_input(
    "TO", value=(pd.Timestamp(max(data['DATE'])).date()), min_value=(pd.Timestamp(min(data['DATE'])).date()), max_value=(pd.Timestamp(max(data['DATE'])).date()))
countries = list(data["COUNTRY"].sort_values().unique())
countries = [x for x in countries if pd.isnull(x) == False]
countries.insert(0, "*")
country = st.sidebar.multiselect("COUNTRY", countries, default="*")
regions = list(data["REGION"].sort_values().unique())
regions = [x for x in regions if pd.isnull(x) == False]
regions.insert(0, "*")
region = st.sidebar.multiselect("REGION", regions, default="*")
perpetrators = list(data["PERPETRATOR"].sort_values().unique())
perpetrators = [x for x in perpetrators if pd.isnull(x) == False]
perpetrators.insert(0, "*")
perpetrator = st.sidebar.multiselect("PERPETRATOR", perpetrators, default="*")
categories = list(data["CATEGORY"].sort_values().unique())
categories = [x for x in categories if pd.isnull(x) == False]
categories.insert(0, "*")
category = st.sidebar.multiselect("CATEGORY", categories, default="*")

mask = (data['DATE'] > np.datetime64(fromdate)) & (
    data['DATE'] <= np.datetime64(todate))
data = data.loc[mask]

if "*" not in country:
    mask = data["COUNTRY"].isin(country)
    data = data[mask]

if "*" not in region:
    mask = data["REGION"].isin(region)
    data = data[mask]

if "*" not in perpetrator:
    mask = data["PERPETRATOR"].isin(perpetrator)
    data = data[mask]

if "*" not in category:
    mask = data["CATEGORY"].isin(category)
    data = data[mask]

lat = []
lon = []
for coord in list(data['COORDINATES'].values):
    try:
        lat.append(coord.split(",")[0])
        lon.append(coord.split(",")[1])
    except:
        continue
callback = """\
function (row) {
    var marker;
    marker = L.circle(new L.LatLng(row[0], row[1]), {color:'red'});
    return marker;
};
"""
make_map_responsive= """
 <style>
 [title~="st.iframe"] { width: 100%}
 </style>
"""
st.markdown(make_map_responsive, unsafe_allow_html=True)

folium_map = folium.Map(tiles='cartodbpositron')
FastMarkerCluster(data=list(zip(lat, lon)),
                  callback=callback).add_to(folium_map)
Fullscreen().add_to(folium_map)
folium_static(folium_map, width=800)
col4, col3 = st.columns([10,90])

freq = col4.radio("Frequency",('DEAD', 'INJURED'))
dist= col4.radio("Distribution",('CATEGORY', 'PERPETRATOR', 'REGION', 'SUBREGION', 'COUNTRY', 'STATE', 'CITY'))

fig = go.Figure(data=[go.Pie(labels=list(data[freq].groupby(data[dist]).sum().sort_values().nlargest(5).index),
                            values=list(data[freq].groupby(
                                data[dist]).sum().sort_values().nlargest(5)))]
                                )

fig.update_traces(hoverinfo='label+percent', textinfo='value', textfont_size=20,
                  marker=dict(line=dict(color='#000000', width=2)))
col3.plotly_chart(fig, use_container_width=True, config = {'displayModeBar': False}
)

st.subheader("DEAD")
fig = go.Figure()
fig.add_trace(go.Scatter(x=data['DATE'], y=data['DEAD'].groupby(data['DATE']).sum()))
st.plotly_chart(fig, use_container_width=True, config = {'displayModeBar': False})

st.subheader("INJURED")
fig = go.Figure()
fig.add_trace(go.Scatter(x=data['DATE'], y=data['INJURED'].groupby(data['DATE']).sum()))
st.plotly_chart(fig, use_container_width=True, config = {'displayModeBar': False})

st.sidebar.title("Statistics")
st.sidebar.text("Attacks: "+str(len(data)) +
                "\nRegions: "+str(len(data["REGION"].unique()))+ "\nCountries: "+str(len(data["COUNTRY"].unique()))+"\nPerpetrators: "+str(len(data["PERPETRATOR"].unique()))+"\nDeaths: "+str(int(data["DEAD"].sum()))+"\nInjuries: "+str(int(data["INJURED"].sum())))
if st.sidebar.button("RERUN"):
    st.experimental_rerun()
st.dataframe(data)

@st.cache
def convert_df(df):
   return df.to_csv().encode('utf-8')


csv = convert_df(data)

st.download_button(
   "DOWNLOAD",
   csv,
   "klapeye-global-terrorism.csv",
   "text/csv",
   key='download-csv'
)
