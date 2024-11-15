import streamlit as st
import plotly.express as px
import pandas as pd
from pinotdb import connect

# Establish the connection
conn = connect(host='54.179.138.51', port=8099, path='/query/sql', schema='http')
curs = conn.cursor()

# Query to get the average price per state
curs.execute('''SELECT 
    STATE,
    AVG(TOTAL_PRICE) AS avg_price_per_state
FROM 3_orders
GROUP BY STATE LIMIT 10;
''')
tables = [row for row in curs.fetchall()]

# Latitude and longitude data
latitude_longitude_dict = {
    'Missouri': {'latitude': 38.573936, 'longitude': -92.60376},
    'Indiana': {'latitude': 39.7684, 'longitude': -86.1581},
    'Illinois': {'latitude': 40.6331, 'longitude': -89.3985},
    'Michigan': {'latitude': 44.3148, 'longitude': -85.6024},
    'Minnesota': {'latitude': 46.7296, 'longitude': -94.6859},
    'Kansas': {'latitude': 39.0119, 'longitude': -98.4842},
    'Ohio': {'latitude': 40.4173, 'longitude': -82.9071},
    'Iowa': {'latitude': 41.8780, 'longitude': -93.0977},
    'Nebraska': {'latitude': 41.1254, 'longitude': -98.2681},
    'Wisconsin': {'latitude': 43.7844, 'longitude': -88.7879}
}

# Convert sales data to DataFrame
states_df = pd.DataFrame(tables, columns=["state", "avg_purchase_amount"])

# Merge latitude and longitude from the dictionary
states_df['latitude'] = states_df['state'].map(lambda x: latitude_longitude_dict.get(x, {}).get('latitude'))
states_df['longitude'] = states_df['state'].map(lambda x: latitude_longitude_dict.get(x, {}).get('longitude'))

# Create a choropleth map using the custom GeoJSON
choropleth_fig = px.choropleth(
    states_df,
    geojson="https://raw.githubusercontent.com/PublicaMundi/MappingAPI/master/data/geojson/us-states.json",
    locations="state",
    featureidkey="properties.name",
    color="avg_purchase_amount",
    color_continuous_scale="Viridis",
    title="Average Purchase Amount by State"
)

choropleth_fig.update_geos(fitbounds="locations")

# Query to get sales by product type
curs.execute('''SELECT 
    PRODUCT_TYPE,
    SUM(TOTAL_PRICE) AS total_sales_by_product
FROM 3_orders
GROUP BY PRODUCT_TYPE LIMIT 10;
''')
tables = [row for row in curs.fetchall()]

# Convert the results into a DataFrame
sales_df = pd.DataFrame(tables, columns=["product_type", "total_sales"])

# Create a pie chart using Plotly
pie_chart_fig = px.pie(sales_df, 
                       names='product_type', 
                       values='total_sales', 
                       title="Sales by Product Type",
                       color='product_type',  
                       color_discrete_sequence=px.colors.qualitative.Set3)

# Query to get page view count by page
curs.execute('''SELECT 
    PAGEID,
    COUNT(*) AS view_count
FROM 1_pageviews
GROUP BY PAGEID
ORDER BY view_count DESC
LIMIT 10;
''')

# Fetch the results into a list of tuples
tables = [row for row in curs.fetchall()]

# Convert the results into a DataFrame
pageview_df = pd.DataFrame(tables, columns=["page_id", "view_count"])

# Create a bar chart using Plotly
bar_chart_fig = px.bar(pageview_df, 
                       x='page_id', 
                       y='view_count', 
                       title="Top Viewed Pages by Users",
                       labels={'page_id': 'Page ID', 'view_count': 'View Count'},  
                       color='page_id',  
                       color_discrete_sequence=px.colors.qualitative.Set3)

# Query to get user orders
curs.execute('''SELECT 
    USERID, 
    COUNT(*) AS ORDER_COUNT, 
    SUM(TOTAL_PRICE) AS TOTAL_PRICE,
    SUM(TOTAL_PRICE) / COUNT(*) AS AVG_PRICE
FROM 3_orders
GROUP BY USERID;''')

# Fetch the results into a DataFrame
user_orders = pd.DataFrame(curs.fetchall(), columns=["USERID", "ORDER_COUNT", "TOTAL_PRICE", "AVG_PRICE"])

# Generate user ids if not present
user_ids = [f"User_{i+1}" for i in range(len(user_orders))]
user_orders['USERID'] = user_ids

# Streamlit Layout with 2 columns and 2 rows
st.title("Data Visualizations")

# First Row: Choropleth and Pie Chart
col1, col2 = st.columns(2)

with col1:
    st.plotly_chart(choropleth_fig)

with col2:
    st.plotly_chart(pie_chart_fig)

# Second Row: Bar Chart and User Orders Table
col3, col4 = st.columns(2)

with col3:
    st.plotly_chart(bar_chart_fig)

with col4:
    st.dataframe(user_orders)
