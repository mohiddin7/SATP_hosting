# SATP incident scraper and dashboard

A Streamlit app for the data side of my event-coding research. It pulls incident summaries from the
[South Asia Terrorism Portal](https://www.satp.org/) (SATP), stores them in Google Sheets, and turns the coded
incidents into an interactive dashboard of where, when and how political violence happens across Indian states.

It belongs to the same project as
[The Limits and Promise of Automated Event Coding: Evidence from the South Asia Terrorism Portal](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=6163986)
(Teitelbaum, Shaik and Sharma, 2026). The models that code each incident live in
[code-satp](https://github.com/eteitelbaum/code-satp).

## What's inside

**Scraper (`app.py`)**

- Pick years (2017 to 2024) and months, and it walks SATP's Maoist insurgency timeline pages for each one.
- Every incident becomes a row with an ID, a date and the cleaned-up summary text. IDs are built from the date
  plus a running number for that day: `I03151701` is the first incident on 15 March 2017.
- Shows the rows in a table, lets you download them as CSV, and can append them to a Google Sheet. Saving is behind
  a password so a public deployment can't write to the sheet.

**Dashboard (`pages/dashboard.py`)**

- Reads the coded incidents from Google Sheets and filters them by state and year.
- Key numbers: incidents, fatalities, injuries, abductions, arrests, surrenders and the deadliest state.
- Charts:
  - incidents over time
  - a choropleth map of India by state
  - actions by type (armed assault, bombing, infrastructure, surrender)
  - a state-by-year heatmap
  - fatalities and injuries over time
  - state rankings
- Exports the filtered rows as CSV.

## Stack

Python, Streamlit, BeautifulSoup, pandas, gspread with a Google service account, plotly, seaborn, matplotlib and
geopandas.

## Run it

```bash
pip install -r requirements.txt
streamlit run app.py
```

The dashboard is the second page in the sidebar. Both pages need a `.streamlit/secrets.toml`:

```toml
scrape_password = "choose-one"

[google_credentials]
# the fields from your Google service account JSON key
type = "service_account"
project_id = "..."
private_key = "..."
client_email = "..."
```

The service account needs edit access to a spreadsheet called `SATP_Data`. The scraper writes to its
`raw_zone_incident_summaries` tab, and the dashboard reads the coded `ALL Data` tab.

There is also a dev container: open the repo in GitHub Codespaces and the app starts on port 8501.
