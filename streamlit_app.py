import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# Function to retrieve floorsheet data
def get_floorsheet_data(as_of=None):
    # Set the URL for the floorsheet API
    url_base = "https://chukul.com/api/data/v2/floorsheet/bydate/?date={{}}&page={{}}&size=120000"
    page_number = 1

    # Create a list to store DataFrames
    all_data_list = []

    # Use the 'as_of' value to set the initial date for the floorsheet API
    initial_date = datetime.strptime(as_of, '%Y-%m-%d').strftime('%Y-%m-%d')

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
            # Break out of the loop for any status code other than 200
            break

    # Concatenate all DataFrames in the list if the list is not empty
    if all_data_list:
        all_data = pd.concat(all_data_list, ignore_index=True)
        return all_data, as_of
    else:
        # Handle the case when no data is retrieved
        return pd.DataFrame(), as_of

# Streamlit UI
st.title("Floorsheet Data")

# Get the current market status 'as_of' value
market_status_url = "https://chukul.com/api/tools/market/status/"
market_status_response = requests.get(market_status_url)

# Check if the request was successful (status code 200)
if market_status_response.status_code == 200:
    market_status_data = market_status_response.json()

    # Get the 'as_of' value from the market status data
    as_of = market_status_data.get("as_of")

    # Button to trigger data retrieval
    if st.button("Retrieve Floorsheet Data"):
        floorsheet_data, latest_as_of = get_floorsheet_data(as_of)

        # Save the data to a CSV file
        csv_file_path = "floorsheet_data.csv"
        floorsheet_data.to_csv(csv_file_path, index=False)

        st.success(f"Click below to download the file")

       # Add a download button for the CSV file
if st.button("Retrieve Floorsheet Data"):
    floorsheet_data, latest_as_of = get_floorsheet_data(as_of)

    # Save the data to a CSV file
    csv_file_path = "floorsheet_data.csv"
    floorsheet_data.to_csv(csv_file_path, index=False)

    st.success(f"Data saved to {csv_file_path}")

    # Add a download button for the CSV file
    csv_data = floorsheet_data.to_csv(index=False)
    st.download_button(
        label="Download CSV File",
        data=csv_data.encode('utf-8'),
        file_name="floorsheet_data.csv",
        mime="text/csv",
        key="download_csv_button"
    )

        )
