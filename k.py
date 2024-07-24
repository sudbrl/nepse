import streamlit as st
import requests
import pandas as pd
from datetime import datetime
from io import BytesIO

# Function to retrieve floorsheet data
def get_floorsheet_data(initial_date, as_of=None):
    url_base = "https://chukul.com/api/data/v2/floorsheet/bydate/?date={}&page={}&size=120000"
    page_number = 1
    all_data_list = []

    while True:
        url = url_base.format(initial_date, page_number)
        if as_of:
            url += f"&as_of={as_of}"

        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            if not data['data']:
                break

            current_data = pd.DataFrame(data['data'])
            as_of = data.get("as_of")
            all_data_list.append(current_data)
            page_number += 1
        else:
            st.error(f"Error retrieving data. Status code: {response.status_code}")
            break

    all_data = pd.concat(all_data_list, ignore_index=True)
    return all_data, as_of

# Function to convert DataFrame to Excel
def convert_df_to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Floorsheet Data')
    processed_data = output.getvalue()
    return processed_data

# Streamlit UI
st.title("Chukul Floorsheet Data")

market_status_url = "https://chukul.com/api/tools/market/status/"
market_status_response = requests.get(market_status_url)

if market_status_response.status_code == 200:
    market_status_data = market_status_response.json()
    as_of = market_status_data.get("as_of")

    if as_of:
        initial_date = datetime.strptime(as_of, '%Y-%m-%d').strftime('%Y-%m-%d')

        if st.button("Retrieve Floorsheet Data"):
            with st.spinner('Retrieving data...'):
                floorsheet_data, latest_as_of = get_floorsheet_data(initial_date, as_of)

            st.success("Data retrieval complete!")

            # Convert DataFrame to Excel
            excel_data = convert_df_to_excel(floorsheet_data)

            st.download_button(
                label="Download Floorsheet Data as Excel",
                data=excel_data,
                file_name='floorsheet_data.xlsx',
                mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            )
    else:
        st.error("Failed to retrieve 'as_of' value from market status data.")
else:
    st.error(f"Failed to retrieve market status. Status code: {market_status_response.status_code}")
