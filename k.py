import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta
from io import StringIO

# Function to retrieve floorsheet data for a given date
def get_floorsheet_data_for_date(selected_date):
    url_base = f"https://chukul.com/api/data/v2/floorsheet/bydate/?date={{}}&page={{}}&size="
    page_number = 1
    all_data = []

    while True:
        url = url_base.format(selected_date.strftime('%Y-%m-%d'), page_number)
        response = requests.get(url, timeout=10)

        if response.status_code == 200:
            data = response.json()

            if not data['data']:
                break

            current_data = pd.DataFrame(data['data'])
            all_data.append(current_data)

            # Check if 'meta' and 'pagination' exist before accessing 'total_pages'
            if 'meta' in data and 'pagination' in data['meta']:
                total_pages = data['meta']['pagination'].get('total_pages', 1)
                if page_number >= total_pages:
                    break
            else:
                # If 'total_pages' doesn't exist, stop the loop
                break

            page_number += 1
        else:
            st.error(f"Data fetch failed. Status code: {response.status_code}")
            return pd.DataFrame()

    if all_data:
        return pd.concat(all_data, ignore_index=True)
    else:
        return pd.DataFrame()

# Function to retrieve floorsheet data within a date range
def get_floorsheet_data(date_from, date_to):
    all_data = []
    
    current_date = date_from
    while current_date <= date_to:
        df = get_floorsheet_data_for_date(current_date)
        if not df.empty:
            all_data.append(df)
        current_date += timedelta(days=1)
    
    if all_data:
        return pd.concat(all_data, ignore_index=True)
    else:
        return pd.DataFrame()

# Streamlit UI
st.title("Floorsheet Download")

# Date range input for the user
date_from = st.date_input("Select Start Date", value=datetime.today() - timedelta(days=1))
date_to = st.date_input("Select End Date", value=datetime.today())

# Button to trigger data retrieval
if st.button("Retrieve Floorsheet Data"):
    with st.spinner("Retrieving floorsheet data..."):
        # Ensure date_from and date_to are datetime objects
        date_from = datetime.strptime(date_from.strftime('%Y-%m-%d'), '%Y-%m-%d')
        date_to = datetime.strptime(date_to.strftime('%Y-%m-%d'), '%Y-%m-%d')

        floorsheet_data = get_floorsheet_data(date_from, date_to)

    if not floorsheet_data.empty:
        # Store the CSV data in StringIO for download
        csv_output = StringIO()
        floorsheet_data.to_csv(csv_output, index=False)
        csv_output.seek(0)

        # Keep displaying the download button until the user downloads the CSV
        st.download_button(
            label="Download CSV",
            data=csv_output.getvalue(),
            file_name="floorsheet_data.csv",
            mime="text/csv"
        )
    else:
        st.warning("No data was retrieved.")
