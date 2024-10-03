# Import libraries
import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit_lottie import st_lottie
import altair as alt
import geopandas as gpd

# Page configuration
st.set_page_config(
    page_title="Indian EV Market",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded")

# Setting Title
st.title(':car: India Ev Market Analysis')
st.markdown('<style>div.block-container{padding-top:2rem;}</style>',unsafe_allow_html=True)

# Reading DataSet
df= pd.read_csv('ev_sales_by_makers_and_cat_15-24.csv')
df1=pd.read_csv('ev_cat_01-24.csv')
df3= pd.read_csv('OperationalPC.csv')
df4=pd.read_csv('EV Maker by Place.csv')

df3['State'] = df3['State'].replace("Odisha", "Orissa")
# Creating minidf
yearly_sales = df.iloc[:, 2:-1].sum()
minidf = pd.DataFrame(yearly_sales).reset_index()
minidf.columns = ['Year', 'Total Sales']

### Converting columns type 
df1['Date'] = df1['Date'].astype(str)
# Step 2: Replace invalid entries with NaT or a placeholder date
df1['Date'] = df1['Date'].replace('0', pd.NaT)  # Replace '0' with NaT
# Step 3: Convert to datetime, specifying the format
df1['Date'] = pd.to_datetime(df1['Date'], format='%m/%d/%y', errors='coerce')

col1, col2 = st.columns((2))
# Getting the min and max date 
startDate = pd.to_datetime(df1["Date"]).min()
endDate = pd.to_datetime(df1["Date"]).max()

# Making StartDate and end date columns
with col1:
    date1 = pd.to_datetime(st.date_input("Start Date", startDate))

with col2:
    date2 = pd.to_datetime(st.date_input("End Date", endDate))

df1= df1[(df1['Date'] >= date1) & (df1['Date'] <= date2)].copy()

st.sidebar.image("CarbonCoders.png")
#st.markdown('<style>div.block-container{padding-top:2rem;}</style>',unsafe_allow_html=True)
st.sidebar.header("Choose your filter: ")
# Create for State
State = st.sidebar.multiselect("Pick your State", df4["State"].unique())
if not State:
    df44=df4.copy()  
else:
    df44=df3[df3['State'].isin(State)]
# Create for Year 
Year = st.sidebar.multiselect("Pick your Year", minidf["Year"].unique())
if not Year:
    minidf1=minidf.copy()  
else:
    minidf1=minidf[minidf['Year'].isin(Year)]
    
if not State:
    filter_data=df4
else:
    filter_data=df4[df4['State'].isin(State)]
    
if not Year:
    filter_Year=minidf
else:
    filter_Year=minidf[minidf['Year'].isin(Year)]

fd1=filter_data['State'].value_counts().reset_index()
fd1.columns = ['State', 'Number of company'] 
    
with col1:
    st.subheader("Total Ev Sales By Year")
    fig = px.bar(filter_Year, x = 'Year', y = 'Total Sales', 
                  template = "seaborn")
    st.plotly_chart(fig,use_container_width=True, height = 200)
with col2:
    st.subheader("EV Plant State Wise")
    fig = px.pie(fd1, values = "Number of company", names = "State", hole = 0.5)
    fig.update_traces(text = fd1["State"], textposition = "outside")
    st.plotly_chart(fig,use_container_width=True)
 
with col1:
     with st.expander("Download Bar Charts Data"):
         st.write(filter_Year.style.background_gradient(cmap="Blues"))
         csv = filter_Year.to_csv(index = False).encode('utf-8')
         st.download_button("Download Data", data = csv, file_name = "Category.csv", mime = "text/csv",
                            help = 'Click here to download the data as a CSV file')

with col2:
     with st.expander("Download Pie Charts Data"):
         st.write(fd1.style.background_gradient(cmap="Oranges"))
         csv = fd1.to_csv(index = False).encode('utf-8')
         st.download_button("Download Data", data = csv, file_name = "state.csv", mime = "text/csv",
                        help = 'Click here to download the data as a CSV file') 
         
df['Growth Rate (%)'] = ((df['2024'] - df['2015']) / df['2015']).replace([float('inf'), -float('inf')], 0) * 100
top_manufacturers_growth = df[['Maker', 'Growth Rate (%)']].sort_values(by='Growth Rate (%)', ascending=False).head(10)          
category_sales = df.groupby('Cat').sum()[['2015', '2016', '2017', '2018', '2019', '2020', '2021','2022', '2023', '2024']].reset_index()
category_sales = df.groupby('Cat').sum().loc[:, '2015':'2024']
category_sales_long = category_sales.reset_index().melt(id_vars='Cat', var_name='Year', value_name='Total Sales')
cat=category_sales_long.groupby('Cat')['Total Sales'].sum().reset_index() 
cat.columns=['Car Category','Total Sales']
chart1, chart2 = st.columns((2))

with chart1:
    st.subheader('Top 10 EV Manufacturers by Growth Rate')
    fig = px.bar(top_manufacturers_growth, x = 'Growth Rate (%)', y = 'Maker', 
                 color_discrete_sequence=['#f4a24b'])
    fig.update_yaxes(autorange='reversed')
    st.plotly_chart(fig,use_container_width=True, height = 200)

with chart2:
    st.subheader('Category wise Sales')
    fig = px.bar(cat, x = 'Car Category', y = 'Total Sales', 
                 color_discrete_sequence=['#4bf465'])
    st.plotly_chart(fig,use_container_width=True)

cl3, cl4 = st.columns((2))
with cl3:
    with st.expander("Download Bar Charts Data"):
        st.write(top_manufacturers_growth.style.background_gradient(cmap="Blues"))
        csv1 = top_manufacturers_growth.to_csv(index = False).encode('utf-8')
        st.download_button("Download Data", data=csv1, file_name="Category1.csv", mime="text/csv", key="unique_key_1")



with cl4:
    with st.expander("Download Bar Charts Data"):
        st.write(cat.style.background_gradient(cmap="Oranges"))
        csv2 = cat.to_csv(index = False).encode('utf-8')
        st.download_button("Download Data", data=csv2, file_name="Category2.csv", mime="text/csv", key="unique_key_2")
        
        
recent_sales = df[['Maker', '2021', '2022', '2023', '2024']]
recent_sales['Total Recent Sales'] = recent_sales[['2021', '2022', '2023', '2024']].sum(axis=1)
emerging_companies = recent_sales[recent_sales['Total Recent Sales'] > 1000]
emerging_companies_sorted = emerging_companies[['Maker', 'Total Recent Sales']].sort_values(by='Total Recent Sales', ascending=False).head(10)
# OLA Sales History
ola_history=df[df['Maker']=='OLA ELECTRIC TECHNOLOGIES PVT LTD']
ola_history.drop(columns=['Cat','Growth Rate (%)'],inplace=True)
ola_history_SUM= ola_history.iloc[:, 2:-1].sum()
minidf_OLA = pd.DataFrame(ola_history_SUM).reset_index()
minidf_OLA.columns = ['Years', 'Total Sales']

cl5, cl6 = st.columns((2))
with cl5:
    st.subheader('Top 10 EV Manufacturers by Sales')
    fig = px.bar(emerging_companies_sorted , x = 'Total Recent Sales', y = 'Maker', 
                 color_discrete_sequence=['#ec4f37'])
    fig.update_yaxes(autorange='reversed')
    st.plotly_chart(fig,use_container_width=True, height = 200)
with cl6:
    st.subheader("OLA'S Exponential Growth History")
    fig = px.line(minidf_OLA, x = 'Years', y = 'Total Sales')
 #   fig.update_yaxes(autorange='reversed')
    st.plotly_chart(fig,use_container_width=True, height = 200)
       
with cl5:
    with st.expander("Download Bar Charts Data"):
        st.write(emerging_companies_sorted.style.background_gradient(cmap="Blues"))
        csv1 = emerging_companies_sorted.to_csv(index = False).encode('utf-8')
        st.download_button("Download Data", data=csv1, file_name="Category1.csv", mime="text/csv", key="unique_key_4")

with cl6:
    with st.expander("Download Line Plot Data"):
        st.write(minidf_OLA.style.background_gradient(cmap="Oranges"))
        csv2 = minidf_OLA.to_csv(index = False).encode('utf-8')
        st.download_button("Download Data", data=csv2, file_name="Category2.csv", mime="text/csv", key="unique_key_6")      
# Heat Map
df_melted = df1.melt(id_vars=["Date"], var_name="Vehicle Type", value_name="Count")

# Create Plotly Heatmap
fig = px.imshow(
    df1.set_index("Date").T,
    labels=dict(x="Date", y="Vehicle Type", color="Count"),
    aspect="auto",
    color_continuous_scale="Cividis"
)

# Update layout
fig.update_layout(
 #   title="Vehicle Data Heatmap",
    template="plotly_dark",
    xaxis_title="Date",
    yaxis_title="Vehicle Type",
    coloraxis_colorbar=dict(title="Count")
)
fig.update_xaxes(showgrid=True, gridcolor='white', gridwidth=2)
fig.update_yaxes(showgrid=True, gridcolor='white', gridwidth=2)
st.title("Vehicle Data Heatmap")
st.plotly_chart(fig)

with st.expander("Download Hitmap Plot Data"):
        st.write(df1.style.background_gradient(cmap="Oranges"))
        csv2 = df1.to_csv(index = False).encode('utf-8')
        st.download_button("Download Data", data=csv2, file_name="Category2.csv", mime="text/csv", key="unique_key_8")

# get some geojson for India.  Reduce somplexity of geomtry to make it more efficient
url = "https://raw.githubusercontent.com/Subhash9325/GeoJson-Data-of-Indian-States/master/Indian_States"
gdf = gpd.read_file(url)
gdf["geometry"] = gdf.to_crs(gdf.estimate_utm_crs()).simplify(1000).to_crs(gdf.crs)
india_states = gdf.rename(columns={"NAME_1": "ST_NM"}).__geo_interface__


# create base map of all India states
fig_choropleth = px.choropleth(
    pd.json_normalize(india_states["features"])["properties.ST_NM"],
    locations="properties.ST_NM",
    geojson=india_states,
    featureidkey="properties.ST_NM",
    color_discrete_sequence=["lightgrey"],
)

# Create the base map for all India states
fig = px.choropleth(
    df3,
    locations='State', 
    geojson=india_states,  
    featureidkey="properties.ST_NM",  
    color='No. of Operational PCS',  
    color_continuous_scale="Viridis", 
    hover_name="State",  
 #   title="No. of Operational PCS by State in India",
)

fig.update_layout(
    template="plotly_dark",
)

fig.update_geos(fitbounds="locations", visible=False)

st.title("Operational PCS in India by State")
st.plotly_chart(fig)  

cl7, cl8 = st.columns((2))

with cl7:
    with st.expander("Download Map Plot Data"):
        st.write(df3.style.background_gradient(cmap="Oranges"))
        csv2 = minidf_OLA.to_csv(index = False).encode('utf-8')
        st.download_button("Download Data", data=csv2, file_name="Category2.csv", mime="text/csv", key="unique_key_11")
        




      