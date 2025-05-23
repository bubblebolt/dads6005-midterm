import time
import streamlit as st
from streamlit_autorefresh import st_autorefresh
import plotly.express as px
import pandas as pd
from pinotdb import connect
from PIL import Image
import requests
from io import BytesIO


# Set Streamlit page configuration for wide layout
st.set_page_config(layout="wide")

if "autorefresh" not in st.session_state:
    st.session_state.autorefresh = True


# Add custom CSS for header with wide layout
st.markdown(
    """
    <style>
    /* General body styling */
    body {
        background-color: #D8DBBD;  /* Body background color */
    }

    /* Main content styling */
    .main {
        background-color: #D8DBBD;  /* Main content background */
        padding-top: 40;  /* Increased padding for more space below the header */
    }

    /* Content container */
    .block-container {
        background-color: #D8DBBD;  /* Content container background */
    }

    /* Custom header styling */
    header[data-testid="stHeader"] {
        background-color: #2A3663;  /* Header background color */
        padding: 10px;  /* Add padding for better appearance */
        display: flex;  /* Flex layout for alignment */
        align-items: center;  /* Center align vertically */
        justify-content: flex-start;  /* Align items to the left */
        width: 100%;  /* Full width */
        position: fixed;  /* Fixed position at the top */
        top: 0;  /* Stick to the top */
        left: 0;  /* Stick to the left */
        z-index: 1000;  /* Ensure it appears above all other content */
    }

    /* Logo styling */
    header img {
        height: 80px;  /* Set logo height */
        margin-right: 20px;  /* Add spacing between logo and title */
    }

    /* Title styling */
    header h1 {
        color: #FAF6E3;  /* Title color */
        font-size: 24px;  /* Title font size */
        margin: 0;  /* Remove margin */
    }

    </style>
    """, 
    unsafe_allow_html=True
)

st.markdown(
    """
    <header data-testid="stHeader">
        <img src="https://raw.githubusercontent.com/bubblebolt/dads/main/DADS5001/ASM4-Dash/Pics/BOBO%20SHOP.png" alt="Logo">  <!-- Use the raw file link -->
        <h1>BoBo Shop Dashboard</h1>
    </header>
    """, 
    unsafe_allow_html=True
)

# Establish the connection
conn = connect(host='54.179.138.51', port=8099, path='/query/sql', schema='http')
curs = conn.cursor()

curs.execute('''
SELECT 
    PRODUCT_TYPE, 
    AVG(UNIT_PRICE) AS AVG_UNIT_PRICE
FROM 
    3_orders
GROUP BY 
    PRODUCT_TYPE; 
''')

current_data = pd.DataFrame(curs.fetchall(), columns=["PRODUCT_TYPE", "AVG_UNIT_PRICE"])

# Initialize session state for previous data
if "previous_data" not in st.session_state:
    st.session_state.previous_data = current_data.copy()

# Calculate delta
merged_data = pd.merge(
    current_data, 
    st.session_state.previous_data, 
    on="PRODUCT_TYPE", 
    how="inner", 
    suffixes=('_current', '_previous')
)
merged_data['DELTA'] = merged_data['AVG_UNIT_PRICE_current'] - merged_data['AVG_UNIT_PRICE_previous']

# Display metrics with color-coded deltas
cols = st.columns(len(merged_data))
for i, (col, row) in enumerate(zip(cols, merged_data.itertuples())):
    col.metric(
        label=f"Product: {row.PRODUCT_TYPE}",
        value=f"${row.AVG_UNIT_PRICE_current:.2f}",
        delta=f"{row.DELTA:+.2f}",
        delta_color="inverse"
    )

# Update previous data with the current data for the next iteration
st.session_state.previous_data = current_data.copy()

# Query for average purchase by state
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
fig1 = px.choropleth(
    states_df,
    geojson="https://raw.githubusercontent.com/PublicaMundi/MappingAPI/master/data/geojson/us-states.json",
    locations="state",
    featureidkey="properties.name",
    color="avg_purchase_amount",
    color_continuous_scale="Viridis"
)

fig1.update_geos(fitbounds="locations")  
fig1.update_layout(
    plot_bgcolor="#D8DBBD",  # Set the plot background color
    paper_bgcolor="#D8DBBD",  # Set the paper (outer) background color
    font=dict(color="black")  # Set the font color to black for better contrast
)

# Query for sales by product type
curs.execute('''SELECT 
    PRODUCT_TYPE,
    SUM(TOTAL_PRICE) AS total_sales_by_product
FROM 3_orders
GROUP BY PRODUCT_TYPE LIMIT 10;
''')

# Fetch the results into a list of tuples
tables = [row for row in curs.fetchall()]

# Convert the results into a DataFrame
sales_df = pd.DataFrame(tables, columns=["product_type", "total_sales"])

# Create a pie chart using Plotly
fig2 = px.pie(sales_df, 
             names='product_type', 
             values='total_sales', 
             color='product_type',  # Color by product type
             color_discrete_sequence=px.colors.qualitative.Set1)  # Set color palette

fig2.update_layout(
    plot_bgcolor="#D8DBBD",  # Set the plot background color
    paper_bgcolor="#D8DBBD",  # Set the paper (outer) background color
    font=dict(color="black")  # Set the font color to black for better contrast
)

# Query for page views
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

# Query for user order details
curs.execute('''SELECT 
    USERID, 
    COUNT(*) AS ORDER_COUNT, 
    SUM(TOTAL_PRICE) AS TOTAL_PRICE,
    SUM(TOTAL_PRICE) /  COUNT(*) AS AVG_PRICE
FROM 3_orders
GROUP BY USERID;
''')

# Fetch data and create a DataFrame for user orders
user_orders = pd.DataFrame(curs.fetchall(), columns=["USERID", "ORDER_COUNT", "TOTAL_PRICE", "AVG_PRICE"])

# Add user IDs if they are not present
user_ids = [f"User_{i+1}" for i in range(len(user_orders))]
user_orders['USERID'] = user_ids

# Display the checkbox with the right position
st.session_state.autorefresh = st.checkbox(
    "Enable Auto-Refresh (5 seconds)🔄", 
    value=st.session_state.autorefresh,
    key="auto_refresh", 
    help="Check this to enable auto-refresh every 5 seconds."
)
# If auto-refresh is enabled, use st_autorefresh
if st.session_state.autorefresh:
    st_autorefresh(interval=5000)


col1, col2 = st.columns(2)

with col1:
    st.subheader("User Orders DataFrame")
    st.dataframe(user_orders, use_container_width=True) 
    
    # Display the multi-select widget first
    st.subheader("Top Viewed Pages by Users")
    selected_pages = st.multiselect(
        "Select Pages to Display",
        options=pageview_df['page_id'].unique(),
        default=pageview_df['page_id'].unique(),  # Default to all pages selected
        help="Select one or more pages to view their data."
    )

    # Filter the DataFrame based on the selected page_ids
    filtered_df = pageview_df[pageview_df['page_id'].isin(selected_pages)]

    # Create and display the filtered bar chart (fig3_filtered)
    fig3_filtered = px.bar(filtered_df, 
                           x='page_id', 
                           y='view_count', 
                           labels={'page_id': 'Page ID', 'view_count': 'View Count'}, 
                           color='page_id', 
                           color_discrete_sequence=px.colors.qualitative.Set1)

    fig3_filtered.update_layout(
        plot_bgcolor="#D8DBBD", 
        paper_bgcolor="#D8DBBD", 
        font=dict(color="black")
    )

    # Plot the bar chart
    st.plotly_chart(fig3_filtered, use_container_width=True)
    
with col2:
    st.subheader("Sales by Product Type")
    st.plotly_chart(fig2, use_container_width=True, height=800)  # Plot the pie chart
    st.subheader("Average Purchase Amount by State")
    st.plotly_chart(fig1, use_container_width=True, height=900)  # Plot the choropleth map


st.header("")



col1, col2, col3, col4 = st.columns(4)

# ฟังก์ชันโหลดภาพจาก URL
def load_image(url):
    response = requests.get(url)
    img = Image.open(BytesIO(response.content))
    return img

# ฟังก์ชันครอปภาพ
def crop_image(image, size=(500, 500)):
    width, height = image.size
    left = (width - size[0]) / 2
    top = (height - size[1]) / 2
    right = (width + size[0]) / 2
    bottom = (height + size[1]) / 2
    cropped_image = image.crop((left, top, right, bottom))
    return cropped_image


# URL ของภาพ
urls = [
    "https://i1.adis.ws/i/canon/eos-r7-lifestyle_c604337a3b374a94a080d40b43f3a920?$70-30-header-4by3-dt-jpg$",
    "https://s2-techtudo.glbimg.com/Aa6RJdKVwf_yn4thohmm3M72tXY=/1200x/smart/filters:cover():strip_icc()/i.s3.glbimg.com/v1/AUTH_08fbf48bc0524877943fe86e43087e7a/internal_photos/bs/2022/S/R/vI6dnhQbmlMgKRx6TSIw/apple-watch-ultra-thassius-veloso-techtudo-02.jpg",
    "https://d30wkz0ptv5pwh.cloudfront.net/media/magefan_blog/mobile_phone.jpg",
    "https://media.cnn.com/api/v1/images/stellar/prod/microsoft-surface-laptop-2024-cnnu-01.jpg?c=16x9&q=h_833,w_1480,c_fill"
]

# โหลดและแสดงภาพในแต่ละคอลัมน์
for i, col in enumerate([col1, col2, col3, col4]):
    with col:
        img = load_image(urls[i])
        cropped_img = crop_image(img, size=(500, 500))  # ครอปภาพให้มีขนาด 500x500
        st.image(cropped_img, width=500)