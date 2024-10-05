# Import libraries
import streamlit as st
import pandas as pd
import plotly.express as px
import requests
from streamlit_lottie import st_lottie
import altair as alt
import geopandas as gpd
from PIL import Image
import base64
from random import randrange
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import st_folium

# 
# import os
# current_dir = os.path.dirname(__file__)

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
df1['Date'] = df1['Date'].replace('0', pd.NaT) 
df1['Date'] = pd.to_datetime(df1['Date'], format='%m/%d/%y', errors='coerce')

# Setting Page Logo
st.sidebar.image("CarbonCoders.png")
# image_path = os.path.join(current_dir, "CarbonCoders.png")
# st.sidebar.image(image_path)
#Creating Side Bar
st.sidebar.header("Choose your filter: ")
# Create for State
State = st.sidebar.multiselect("Pick your State", df4["State"].unique())
if not State:
    df44=df4.copy()  
else:
    df44=df3[df3['State'].isin(State)]
# Create for Year 
Year = st.sidebar.multiselect("Pick your Year", minidf["Year"].unique())

# Creating Filter Logic
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
# Some Vizualisation 
col1, col2 = st.columns((2))    
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
         
st.markdown("<br>", unsafe_allow_html=True)  # Adds a line break
st.markdown("<br>", unsafe_allow_html=True)  # Adds a line break

# Some visualization         
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

st.markdown("<br>", unsafe_allow_html=True)  # Adds a line break
st.markdown("<br>", unsafe_allow_html=True)  # Adds a line break

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
        

# Vehicle Data Heatmap
st.markdown("<br>", unsafe_allow_html=True)  # Adds a line break
st.markdown("<br>", unsafe_allow_html=True)  # Adds a line break

st.markdown("<h3 style='text-align: center;'>Vehicle Data Heatmap</h3>", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)  # Adds a line break

coll1, coll2 = st.columns((2))
# Getting the min and max date 
startDate = pd.to_datetime(df1["Date"]).min()
endDate = pd.to_datetime(df1["Date"]).max()

# Making StartDate and end date columns
with coll1:
    date1 = pd.to_datetime(st.date_input("Start Date", startDate))

with coll2:
    date2 = pd.to_datetime(st.date_input("End Date", endDate))

df1= df1[(df1['Date'] >= date1) & (df1['Date'] <= date2)].copy()      
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
st.markdown("<br>", unsafe_allow_html=True)  # Adds a line break
st.markdown("<br>", unsafe_allow_html=True)  # Adds a line break

st.markdown("<h3 style='text-align: center;'>Operational PCS in India by State</h3>", unsafe_allow_html=True)
st.plotly_chart(fig)  

cl7, cl8 = st.columns((2))

with cl7:
    with st.expander("Download Map Plot Data"):
        st.write(df3.style.background_gradient(cmap="Oranges"))
        csv2 = minidf_OLA.to_csv(index = False).encode('utf-8')
        st.download_button("Download Data", data=csv2, file_name="Category2.csv", mime="text/csv", key="unique_key_11")


# ev_makers
# Load Data from CSV
@st.cache_data
def load_data():
    try:
        data = pd.read_csv('EV_Maker_with_Location.csv')
    except Exception as e:
        st.error(f"Error loading CSV file: {e}")
        return pd.DataFrame()  # Returning empty DataFrame if error occurs
    
    # Necessary columns
    required_columns = ['EV Maker', 'Place', 'State', 'Latitude', 'Longitude']
    if not all(col in data.columns for col in required_columns):
        st.error("CSV file must contain columns: EV Maker, Place, State, Latitude, Longitude")
        return pd.DataFrame()  # Returning empty DataFrame if columns are missing
    
    # Converting Latitude and Longitude to numeric
    data['Latitude'] = pd.to_numeric(data['Latitude'], errors='coerce')
    data['Longitude'] = pd.to_numeric(data['Longitude'], errors='coerce')

    # Dropping rows with missing values in Latitude or Longitude
    data = data.dropna(subset=['Latitude', 'Longitude'])
    
    return data

# Main Streamlit App
def main():
    st.markdown("<br>", unsafe_allow_html=True)  # Adds a line break
    st.markdown("<br>", unsafe_allow_html=True)  # Adds a line break
    st.markdown("<h3 style='text-align: center;'>Explore the Electric Vehicle Makers Location in India</h3>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)  # Adds a line break

    data = load_data()
    if data.empty:
        return  # Exit if data is not valid

    # Filter valid latitude and longitude ranges
    data = data[(data['Latitude'].between(-90, 90)) & (data['Longitude'].between(-180, 180))]

    
    # columns for filter options and map
    col1, col2 = st.columns([1, 2])  # Adjustment of proportions as needed

    with col1:
        # horizontal layout for the logo and header
        # st.image(logo_path, width=30, caption='')  # Display the logo
        st.markdown("<h3 style='margin: 0;'>Filter Options</h3>", unsafe_allow_html=True)
        selected_maker = st.multiselect("Select EV Maker", options=data['EV Maker'].unique())
        selected_place = st.multiselect("Select Place", options=data['Place'].unique())
        selected_state = st.multiselect("Select State", options=data['State'].unique())

    # Filter data based on selections
    if selected_maker:
        data = data[data['EV Maker'].isin(selected_maker)]
    if selected_place:
        data = data[data['Place'].isin(selected_place)]
    if selected_state:
        data = data[data['State'].isin(selected_state)]

    # Create a Folium map centered around India
    india_map = folium.Map(location=[20.5937, 78.9629], zoom_start=5)

    # Add data points to the map
    marker_cluster = MarkerCluster().add_to(india_map)

    for _, row in data.iterrows():
        folium.Marker(
            location=[row['Latitude'], row['Longitude']],
            popup=f"{row['EV Maker']} at {row['Place']} ({row['State']})",
            tooltip=f"{row['EV Maker']} at {row['Place']}",
            icon=folium.Icon(color='blue')
        ).add_to(marker_cluster)

    # Render the map in the second column
    with col2:
        st_folium(india_map, width=700, height=500)

if __name__ == "__main__":
    main()


# Function to generate car image 
def create_car_image(body_type, color, wheels, roof):
    base_image_path = f'assets/{body_type.lower()}_{color.lower()}.png'  
    car_image = Image.open(base_image_path)
    return car_image

# Custom function for encoding and downloading car image
def imagedownload(filename):
    image_file = open(filename, 'rb')
    b64 = base64.b64encode(image_file.read()).decode()  
    href = f'<a href="data:image/png;base64,{b64}" download={filename}>Download {filename} File</a>'
    return href

# Lottie animation function
def load_lottieurl(url: str):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

# Main Page Title
st.markdown("<br>", unsafe_allow_html=True)  # Adds a line break
st.markdown("<br>", unsafe_allow_html=True)  # Adds a line break

st.subheader("Choose Best EV Car for You")

st.markdown("<br>", unsafe_allow_html=True)  # Adds a line break

# Car customization options
list_car_body_type = ['SEDAN', 'SUV']
list_car_color = ['RED', 'BLUE', 'BLACK', 'WHITE', 'GREEN', 'YELLOW', 'SILVER']
list_wheel_type = ['ALLOY', 'STEEL', 'SPORT', 'CHROME']
list_roof_type = ['DEFAULT', 'SUNROOF']

# Random selection or default selection
if st.button('Random Car'):
    index_car_body_type = randrange(0, len(list_car_body_type))
    index_car_color = randrange(0, len(list_car_color))
    index_wheel_type = randrange(0, len(list_wheel_type))
    index_roof_type = randrange(0, len(list_roof_type))
else:
    index_car_body_type = 0
    index_car_color = 0
    index_wheel_type = 0
    index_roof_type = 0

# Create columns for filters and car image
col1, col2 = st.columns([1, 2])  # Adjusting column width

with col1:
    # CSS to adjust the width of the select boxes
    st.markdown(
        """
        <style>
        .small-select {
            width: 150px;
        }
        </style>
        """, unsafe_allow_html=True
    )

    # User-selected options with class for small width
    option_car_body_type = st.selectbox('Car Body Type', list_car_body_type, index=index_car_body_type, key="body_type")
    option_car_color = st.selectbox('Car Color', list_car_color, index=index_car_color, key="color")
    option_wheel_type = st.selectbox('Wheel Type', list_wheel_type, index=index_wheel_type, key="wheels")
    option_roof_type = st.selectbox('Roof Type', list_roof_type, index=index_roof_type, key="roof")

with col2:
    # Generate car image based on selected options
    car_image = create_car_image(option_car_body_type, option_car_color, option_wheel_type, option_roof_type)
    st.markdown("<h4 style='text-align: center;'>Best Option for You </h4>", unsafe_allow_html=True)

    st.image(car_image, use_column_width=True)  # Use the entire column width

# Download section
c20, c21 = st.columns((2))
with c20:
    with st.expander("Download Car Details"):
        car_image.save('custom_car.png')
        st.markdown(imagedownload('custom_car.png'), unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)  # Adds a line break
st.markdown("<br>", unsafe_allow_html=True)  # Adds a line break

# About us section
lottie_hello = load_lottieurl("https://lottie.host/64aa95f8-caec-4d90-ad50-2ac0759715ca/VYBvpn5NAI.json")       
c22, c23 = st.columns((2))
with c22:
    st.markdown("""# :male-student: What We Do
This project analyzes the Indian EV market from 2001-2024, focusing on growth trends, 
policies, infrastructure, key players, sales data, and consumer preferences. It provides 
insights into market drivers, challenges, and future prospects, offering a concise view of 
India's EV evolution.

**Done By**
\n:one: Souvik Samanta 
\n:two: Saurabh Subhash Tehare
\n:three: Arafat Wakeel Khan
\n:four: Prajwal Nikure
\n:five: Busetty Vasavi
\n Thanks :heartpulse:
""")
    
with c23:
    st_lottie(
        lottie_hello,
        speed=1,
        reverse=False,
        loop=True,
        quality="low", 
        height=None,
        width=None,
        key=None,
    )

# End 



      