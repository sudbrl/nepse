import streamlit as st
import requests
import pandas as pd
from datetime import datetime
from io import BytesIO

# Function to retrieve floorsheet data
@st.cache_data()
def get_floorsheet_data(selected_date, as_of=None, max_pages=10):
    # Set the URL for the floorsheet API
    url_base = f"https://chukul.com/api/data/v2/floorsheet/bydate/?date={{}}&page={{}}&size=5000"
    page_number = 1
    all_data = []

    while page_number <= max_pages:
        url = url_base.format(selected_date, page_number)

        # Include as_of parameter if it's available
        if as_of:
            url += f"&as_of={as_of}"

        # Make a GET request to the API with a timeout
        response = requests.get(url, timeout=10)

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            # Parse the JSON data from the response
            data = response.json()

            # Display page number and data size
            st.write(f"Retrieved page {page_number}, data size: {len(data['data'])}")

            # Check if 'data' is empty, indicating no more records
            if not data['data']:
                st.warning("No more records found.")
                break

            # Extract information from the data
            current_data = pd.DataFrame(data['data'])

            # Update as_of with the latest value
            as_of = data.get("as_of")

            # Append the current data to the list
            all_data.append(current_data)

            # Increment the page number for the next iteration
            page_number += 1
        else:
            st.error(f"Data fetch failed. Status code: {response.status_code}")
            break

    if all_data:
        # Concatenate all DataFrames in the list
        df = pd.concat(all_data, ignore_index=True)
        st.write(f"Total records retrieved: {len(df)}")
    else:
        df = pd.DataFrame()
        st.warning("No data was retrieved.")

    return df, as_of

# Streamlit UI
st.title("Floorsheet Download")

# Date input for user to specify the date
selected_date = st.date_input("Select Date", value=datetime.today()).strftime('%Y-%m-%d')

# Button to trigger data retrieval
if st.button("Retrieve Floorsheet Data"):
    with st.spinner("Retrieving floorsheet data..."):
        # Call the function to get floorsheet data
        floorsheet_data, latest_as_of = get_floorsheet_data(selected_date, max_pages=10)

        # Display a message outside the cached function
        if not floorsheet_data.empty:
            st.success("Data retrieval successful.")
            st.dataframe(floorsheet_data)

            # Convert DataFrame to CSV format
            output = BytesIO()
            floorsheet_data.to_csv(output, index=False)
            output.seek(0)

            # Create a download button for CSV file
            st.download_button(
                label="Download CSV",
                data=output,
                file_name="floorsheet_data.csv",
                mime="text/csv"
            )
        else:
            st.warning("No data to display or download.")
