import streamlit as st
import requests
import pandas as pd
from datetime import datetime
from io import BytesIO

# Function to retrieve floorsheet data
@st.cache_data
def get_floorsheet_data(as_of=None):
    # Set the URL for the floorsheet API
    url_base = "https://chukul.com/api/data/v2/floorsheet/bydate/?date={}&page={}&size=120000"
    page_number = 1

    # Create a list to store DataFrames
    all_data_list = []

    while True:
        url = url_base.format(initial_date, page_number)

        # Include as_of parameter if it's available
        if as_of:
            url += f"&as_of={as_of}"

        # Make a GET request to the API
        response = requests.get(url)

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            # Parse the JSON data from the response
            data = response.json()

            # Check if 'data' is empty, indicating no more records
            if not data['data']:
                break

            # Extract information from the data
            current_data = pd.DataFrame(data['data'])

            # Update as_of with the latest value
            as_of = data.get("as_of")

            # Append the current data to the list
            all_data_list.append(current_data)

            # Increment the page number for the next iteration
            page_number += 1
        else:
            st.error(f"Data fetching failed. Status code: {response.status_code}")
            break

    # Concatenate all DataFrames in the list
    all_data = pd.concat(all_data_list, ignore_index=True)

    return all_data, as_of

# Streamlit UI
st.title("Floorsheet Download")

# Get the current market status 'as_of' value
market_status_url = "https://chukul.com/api/tools/market/status/"
market_status_response = requests.get(market_status_url)

# Check if the request was successful (status code 200)
if market_status_response.status_code == 200:
    market_status_data = market_status_response.json()

    # Get the 'as_of' value from the market status data
    as_of = market_status_data.get("as_of")

    # Use the 'as_of' value to set the initial date for the floorsheet API
    initial_date = datetime.strptime(as_of, '%Y-%m-%d').strftime('%Y-%m-%d')

    # Button to trigger data retrieval
    if st.button("Retrieve Floorsheet Data"):
        with st.spinner("Retrieving data..."):
            floorsheet_data, latest_as_of = get_floorsheet_data(as_of)

        # Display a message outside the cached function
        st.write("Data retrieval successful.")

        # Provide a download link for the XLSX file
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            floorsheet_data.to_excel(writer, index=False, sheet_name='Floorsheet Data')
        xlsx_data = output.getvalue()
        
        st.download_button(
            label="Download XLSX",
            data=xlsx_data,
            file_name="floorsheet_data.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
else:
    st.error("Failed to fetch market status data.")
