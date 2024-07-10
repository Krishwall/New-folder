# streamlit run dashboard.py
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import time

# global variables
years = list(map(str, range(1980, 2014)))

@st.cache_data
def load_data():
    df = pd.read_excel("Canada.xlsx", sheet_name=1, skiprows=20, skipfooter=2)

    
    cols_to_rename ={
    'OdName': 'Country',
    'AreaName': 'Continent',
    'RegName': 'Region',
    'DevName': 'Status',
    }
    df = df.rename(columns=cols_to_rename)
    cols_to_drop = ['AREA', 'REG', 'DEV', 'Type', 'Coverage']
    df = df.drop(columns=cols_to_drop)
    df = df.set_index('Country')
    df.columns = [str(name).lower() for name in df.columns.tolist()]
    df['total'] = df[years].sum(axis=1)
    df=df.sort_values(by='total',ascending=False)
    # renaming countries
    df = df.rename(index={'United Kingdom of Great Britain and Northern Ireland': 'UK'})
    df = df.rename(index={'Iran (Islamic Republic of)': 'Iran'})
    df = df.rename(index={'United States of America': 'USA'})

    return df
# configure the layout
st.set_page_config(
    layout='wide',
    page_title='Immigration Data Analysis',
    page_icon="📊",
    initial_sidebar_state="collapsed"
)
#loading the data
with st.spinner(" Loading Data..."):
   # time.sleep(5)
    df=load_data()
    st.sidebar.success("Data Loaded successfully")
# creating the UI interface
c1,c2,c3=st.columns([2,1,1])
c1.title("Canada Immigration Analysis")
c2.header("Summary of data")
total_rows=df.shape[0]
total_cols=df.shape[1]
total_immig=df.total.sum()
max_immig=df.total.max()
max_immig_country=df.total.idxmax()

c2.metric("Total Countries",total_rows)
c2.metric("Total Years",len(years))
c2.metric("Total Immigration",f'{total_immig/1000000: .2f}M')
c2.metric("Maximum Immigration",f'{max_immig/1000000: .2f}M',
          f"{max_immig_country}")
c3.header("TOP 10 Countries")
top_10=df.head(10)['total']
c3.dataframe(top_10,use_container_width=True)
figtop10=px.bar(top_10,x=top_10.index,y='total')
#c3.plotly_chart(figtop10,use_container_width=True)

# country wise visualisation
countries= df.index.to_list()
country=c1.selectbox("Select a Country",countries)
immig=df.loc[country,years]
fig=px.area(immig,x=immig.index,y= immig.values,title="Immigration trend")

c1.plotly_chart(fig,use_container_width=True)
fig2=px.histogram(immig,x=immig.values,nbins=10,marginal="box",)


max_immig_for_country=immig.max()
max_year=immig.idxmax()
c2.metric(f"Max Immigration for {country}",
          f"{max_immig_for_country/1000 :.2f}K",
          f"{max_year}")
c1,c2=st.columns(2)
c1.plotly_chart(fig2,use_container_width=True)
c2.plotly_chart(figtop10,use_container_width=True)

st.header("Continent Wise Analysis")
c1,c2=st.columns(2)
continents=df['continent'].unique().tolist()
cdf=df.groupby('continent')[years].sum() 
cdf['total']=cdf.sum(axis=1)

#c1.dataframe(cdf,use_container_width=True)
figContinent=px.pie(cdf,names=cdf.index,values='total',
                    title='Continent Wise Immigration',
                    hole=.5,
                    height=700)

c1.plotly_chart(figContinent,use_container_width=True,)
#mapContinent= px.scatter_geo(df,locations='continent')

figMap=px.choropleth(df,
                     locations=df.index,
                     locationmode='country names',
                     color='total',
                     title='World Map',
                     projection='natural earth',
                     width=1200, height=800,
                     template='plotly_dark',)
st.plotly_chart(figMap,use_container_width=True)