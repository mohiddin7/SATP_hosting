import json
import streamlit as st
import pandas as pd
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

def main():
    st.set_page_config(
        page_title="Political Incident Dashboard",
        page_icon="📊",
        layout="wide"
    )

    st.title("📊 Political Incident Research Dashboard")
    st.markdown("Gain insights into incidents across regions and time with advanced visualizations for political research.")

    # Load the dataset
    @st.cache_data
    # Function to fetch data from Google Sheets
    def fetch_data_from_google_sheets(spreadsheet_name, sheet_name):
        # Set up Google Sheets API credentials
        SCOPES = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
        service_account_info = st.secrets["google_credentials"]
        creds = Credentials.from_service_account_info(service_account_info, scopes=SCOPES)
        client = gspread.authorize(creds)

        # Open the spreadsheet and worksheet
        sheet = client.open(spreadsheet_name).worksheet(sheet_name)

        # Fetch all data into a DataFrame
        data = pd.DataFrame(sheet.get_all_records())
        # Convert Date column to datetime
        data['Date'] = pd.to_datetime(data['Date'], errors='coerce')
        data['year'] = data['Date'].dt.year
        #
        return data

    spreadsheet_name = "SATP_Data"
    sheet_name = "ALL Data"
    data = fetch_data_from_google_sheets(spreadsheet_name, sheet_name)

    # Sidebar for filters
    st.sidebar.header("Filters")
    selected_state = st.sidebar.multiselect(
        "Select State", options=data['state'].unique(), default=data['state'].unique()
    )

    # Handle single year case for the slider
    if data['year'].nunique() > 1:
        selected_year = st.sidebar.slider(
            "Select Year Range",
            int(data['year'].min()),
            int(data['year'].max()),
            (int(data['year'].min()), int(data['year'].max()))
        )
    else:
        only_year = data['year'].iloc[0]
        selected_year = (only_year, only_year)
        st.sidebar.info(f"Data available for only one year: {only_year}")

    # Filter the data
    filtered_data = data[
        (data['state'].isin(selected_state)) & 
        (data['year'].between(*selected_year))
    ]

    # Display filtered data
    st.header("Filtered Data")
    st.dataframe(filtered_data, height=300)

    # 1. Incident Trend Over Time
    st.header("📈 Trend of Incidents Over Time")
    trend_data = filtered_data.groupby(["Date", "state"]).size().reset_index(name="Incident Count")
    fig_trend = px.line(
        trend_data, 
        x="Date", y="Incident Count", color="state",
        title="Daily Incident Trend by State"
    )
    st.plotly_chart(fig_trend)

    # 2. Geographic Distribution of Incidents
    st.header("🗺️ Geographic Distribution of Incidents")
    state_counts = filtered_data.groupby("state").size().reset_index(name="Incident Count")
    geojson_file_path = r"india-states.json"  # Replace with actual GeoJSON path
    try:
        with open(geojson_file_path, "r") as file:
            india_geojson = json.load(file)
        geojson_states = [feature['properties']['ST_NM'] for feature in india_geojson['features']]
        state_counts = state_counts[state_counts['state'].isin(geojson_states)]
        fig_geo = px.choropleth_mapbox(
            state_counts,
            geojson=india_geojson,
            locations="state",
            featureidkey="properties.ST_NM",
            color="Incident Count",
            title="State-wise Incident Distribution",
            color_continuous_scale="Viridis",
            mapbox_style="carto-positron",
            center={"lat": 22.9734, "lon": 78.6569},
            zoom=4.5,
            opacity=0.6,
        )
        st.plotly_chart(fig_geo)
    except FileNotFoundError:
        st.error("GeoJSON file not found. Please update the file path.")

    # 3. Actions and Perpetrators
    st.header("🎯 Actions by Perpetrators")
    action_columns = [
        "action_armed_assault", "action_bombing", 
        "action_infrastructure", "action_surrender"
    ]
    action_counts = filtered_data[action_columns].sum()
    fig_actions = px.bar(
        action_counts, 
        x=action_counts.index, y=action_counts.values, 
        title="Distribution of Actions by Type",
        labels={"x": "Action Type", "y": "Count"}
    )
    st.plotly_chart(fig_actions)

    # # 4. Word Cloud of Incident Summaries
    # st.header("☁️ Word Cloud of Incident Summaries")
    # all_text = " ".join(filtered_data['Incident_Summary'].dropna())
    # wordcloud = WordCloud(
    #     background_color='white', width=800, height=400
    # ).generate(all_text)
    # fig_wc, ax = plt.subplots(figsize=(12, 6))
    # ax.imshow(wordcloud, interpolation='bilinear')
    # ax.axis("off")
    # st.pyplot(fig_wc)

    # 5. Heatmap of Incidents by State and Year
    st.header("🔥 Heatmap of Incidents by State and Year")
    heatmap_data = filtered_data.groupby(["state", "year"]).size().unstack(fill_value=0)
    fig, ax = plt.subplots(figsize=(14, 8))
    sns.heatmap(heatmap_data, annot=True, fmt="d", cmap="coolwarm", ax=ax)
    st.pyplot(fig)

    # 6. Fatalities and Injuries Over Time
    st.header("📊 Fatalities and Injuries Over Time")
    fatality_data = filtered_data.groupby("Date")[["total_fatalities", "total_injuries"]].sum().reset_index()
    fig_fatalities = px.bar(
        fatality_data, 
        x="Date", y=["total_fatalities", "total_injuries"], 
        title="Daily Fatalities and Injuries",
        labels={"value": "Count", "Date": "Date"}, barmode="group"
    )
    st.plotly_chart(fig_fatalities)

    # Download Button for Filtered Data
    st.sidebar.header("📥 Download Filtered Data")
    if st.sidebar.button("Download CSV"):
        filtered_data.to_csv("filtered_data.csv", index=False)
        st.sidebar.success("Filtered data saved as 'filtered_data.csv'.")

if __name__ == "__main__":
    main()
