import streamlit as st
import requests
import pandas as pd
from datetime import datetime
from io import StringIO

# Function to retrieve floorsheet data
@st.cache_data()
def get_floorsheet_data(selected_date, max_pages=10):
    url_base = f"https://chukul.com/api/data/v2/floorsheet/bydate/?date={{}}&page={{}}&size=5000"
    page_number = 1
    all_data = []

    while page_number <= max_pages:
        url = url_base.format(selected_date, page_number)
        response = requests.get(url, timeout=10)

        if response.status_code == 200:
            data = response.json()

            if not data['data']:
                break

            current_data = pd.DataFrame(data['data'])
            all_data.append(current_data)
            page_number += 1
        else:
            st.error(f"Data fetch failed. Status code: {response.status_code}")
            break

    if all_data:
        df = pd.concat(all_data, ignore_index=True)
    else:
        df = pd.DataFrame()

    return df

# Streamlit UI
st.title("Floorsheet Download")

# Date input for user to specify the date
selected_date = st.date_input("Select Date", value=datetime.today()).strftime('%Y-%m-%d')

# Button to trigger data retrieval
if st.button("Retrieve Floorsheet Data"):
    with st.spinner("Retrieving floorsheet data..."):
        floorsheet_data = get_floorsheet_data(selected_date)

    if not floorsheet_data.empty:
        st.success("Data retrieval successful.")

        # Store the CSV data in StringIO for download
        csv_output = StringIO()
        floorsheet_data.to_csv(csv_output, index=False)
        csv_output.seek(0)

        # Display the download button
        st.download_button(
            label="Download CSV",
            data=csv_output.getvalue(),
            file_name="floorsheet_data.csv",
            mime="text/csv"
        )
    else:
        st.warning("No data was retrieved.")
