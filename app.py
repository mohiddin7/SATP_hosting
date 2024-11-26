##%%writefile app.py
import json
import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import matplotlib.pyplot as plt

# Function to fetch data from Google Sheets
def fetch_data_from_google_sheets(spreadsheet_name, sheet_name):
    # Set up Google Sheets API credentials
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
    service_account_info = st.secrets["google_credentials"]
    creds = Credentials.from_service_account_file(
        'service_account_info', 
        scopes=SCOPES
    )
    client = gspread.authorize(creds)

    # Open the spreadsheet and worksheet
    sheet = client.open(spreadsheet_name).worksheet(sheet_name)

    # Fetch all data into a DataFrame
    data = pd.DataFrame(sheet.get_all_records())
    return data

# Streamlit app
def main():
    st.title("Event Analysis: Number of Events by Month")

    # Get data from Google Sheets
    spreadsheet_name = "SATP_Data"
    sheet_name = "2017"
    data = fetch_data_from_google_sheets(spreadsheet_name, sheet_name)

    # Convert Date column to datetime
    data['Date'] = pd.to_datetime(data['Date'])

    # Extract month and year for grouping
    data['Month'] = data['Date'].dt.month
    data['Year'] = data['Date'].dt.year

    # Count events by month
    monthly_counts = data.groupby('Month').size().reset_index(name='Event Count')

    # Plot histogram
    fig, ax = plt.subplots()
    ax.bar(monthly_counts['Month'], monthly_counts['Event Count'], tick_label=monthly_counts['Month'])
    ax.set_title('Number of Events by Month')
    ax.set_xlabel('Month')
    ax.set_ylabel('Event Count')

    # Show the plot in Streamlit
    st.pyplot(fig)

    # Show the data table
    st.subheader("Monthly Event Counts")
    st.dataframe(monthly_counts)

if __name__ == "__main__":
    main()
