##%%writefile app.py
import json
import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import matplotlib.pyplot as plt



import streamlit as st
import requests
from bs4 import BeautifulSoup
import re
import pandas as pd

def scrape_satp_data(base_url, years, months):
    data = []

    #headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"}
    headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    }

    for year in years:
      for month in months:
          url = f"{base_url}-{month}-{year}"
          print(f"Scraping: {url}")
          response = requests.get(url)
          # response = requests.get(url, headers=headers)
          if response.status_code != 200:
              print(f"Failed to fetch data for {month}: {response.status_code}")
              continue

          soup = BeautifulSoup(response.text, 'html.parser')

          # Extract incident details and dates
          coverpage_news = soup.find_all('div', class_='more')  # Incidents
          coverpage_date = soup.find_all('td', style="width: 15%;")  # Dates

          # Validate counts of incidents and dates
          if len(coverpage_news) != len(coverpage_date):
              print(f"Warning: Mismatch in dates ({len(coverpage_date)}) and incidents ({len(coverpage_news)}) for {month}.")
              continue

          # Group incidents by date to track the nn counter
          incidents_by_date = {}

          # Iterate through the extracted dates and incidents
          for date, incident in zip(coverpage_date, coverpage_news):
              # Clean and format the incident summary
              incident_summary = incident.get_text().strip()
              incident_summary = re.sub(r"\s+", " ", incident_summary)  # Remove extra whitespace
              incident_summary = incident_summary.replace("Read less...", "")  # Remove "Read less..."

              # Clean and format the date
              raw_date = date.get_text().strip()
              day = raw_date.split('-')[-1].strip()
              month_number = f"{months.index(month) + 1:02}"  # Convert month name to two-digit number
              formatted_date = f"{year}-{month_number}-{day.zfill(2)}"

              # Track the nn counter for this date
              if formatted_date not in incidents_by_date:
                  incidents_by_date[formatted_date] = 0
              incidents_by_date[formatted_date] += 1

              # Generate the incident number in mmddyynn format
              nn = f"{incidents_by_date[formatted_date]:02}"  # Increment counter for each summary
              incident_number = f"{month_number}{day.zfill(2)}{year[-2:]}{nn}"
              incident_number = int(incident_number)

              # Append to the data list
              data.append({
                  "Incident_Number": incident_number,
                  "Date": formatted_date,
                  "Incident_Summary": incident_summary
              })

      # Convert the data to a pandas DataFrame
    return pd.DataFrame(data), len(data)

base_url = "https://www.satp.org/terrorist-activity/india-maoistinsurgency"
years = ["2017","2018"]
months = ["Jan","Feb"]
# Scrape data
scraped_data,l = scrape_satp_data(base_url, years, months)
print(f"Total Incidents Scraped: {l}")


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
    return data

# Streamlit app
def main():
    st.title("Event Analysis: Number of Events by Month")

    # Get data from Google Sheets
    spreadsheet_name = "SATP_Data"
    sheet_name = "raw_zone_incident_summaries"
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
    st.dataframe(scraped_data)

if __name__ == "__main__":
    main()
