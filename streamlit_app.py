import streamlit as st
import requests
import pandas as pd
from datetime import datetime
from io import BytesIO

# Function to retrieve floorsheet data
@st.cache_data()
def get_floorsheet_data(initial_date, as_of=None):
    url_base = f"https://chukul.com/api/data/v2/floorsheet/bydate/?date={{}}&page={{}}&size=120000"
    page_number = 1
    all_data = []

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
            all_data.append(current_data)
            page_number += 1
        else:
            break

    df = pd.concat(all_data, ignore_index=True) if all_data else pd.DataFrame()
    return df, as_of

# Streamlit UI
st.title("Floorsheet Download")

market_status_url = "https://chukul.com/api/tools/market/status/"
market_status_response = requests.get(market_status_url)

if market_status_response.status_code == 200:
    market_status_data = market_status_response.json()
    as_of = market_status_data.get("as_of")
    initial_date = datetime.strptime(as_of, '%Y-%m-%d').strftime('%Y-%m-%d')

    if st.button("Retrieve Floorsheet Data"):
        floorsheet_data, latest_as_of = get_floorsheet_data(initial_date, as_of)

        if not floorsheet_data.empty:
            output = BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                floorsheet_data.to_excel(writer, index=False)
            output.seek(0)

            st.download_button(
                label="Download Excel",
                data=output,
                file_name="floorsheet_data.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            st.success("Data retrieval successful. You can download the Excel file.")
else:
    st.error("Failed to fetch market status data.")
