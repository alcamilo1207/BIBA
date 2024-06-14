import requests
import json
import pandas as pd
import streamlit as st
from datetime import datetime,timedelta

def get_prices():
    # Define the URL to send the request to
    url = 'https://www.smard.de/nip-download-manager/nip/download/market-data'  # Replace with the actual URL

    # Define the headers for the request
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json, text/plain, */*'
    }

    # Get the current date and time
    now = datetime.now()

    # Get the current day datetime starting at 00:00 hours
    current_day_start = datetime(now.year, now.month, now.day, 0, 0, 0)

    # Get the next day datetime starting at 00:00 hours
    next_day_start = current_day_start + timedelta(days=1)


    # Format the datetimes as strings for better readability
    current_datetime_str = current_day_start.strftime("%Y-%m-%d %H:%M:%S")
    next_day_datetime_str = next_day_start.strftime("%Y-%m-%d %H:%M:%S")

    # Print the current datetime and the next day's datetime
    st.write("Current datetime:", current_datetime_str)
    st.write("Next day's datetime:", next_day_datetime_str)

    st.write("Current datetime integer:", int(current_day_start.timestamp()))
    st.write("Next day's datetime:", int(next_day_start.timestamp()))

    start_date = int(current_day_start.timestamp())
    end_date = int(next_day_start.timestamp())

    # Define the data to be sent in the request
    data = {"request_form":[{"format":"CSV","moduleIds":[8004169,8004170,8000251,8005078,8000252,8000253,8000254,8000255,8000256,8000257,8000258,8000259,8000260,8000261,8000262,8004996,8004997],"region":"DE","timestamp_from":start_date,"timestamp_to":end_date,"type":"discrete","language":"en","resolution":"hour"}]}

    # Convert the data dictionary to a JSON string
    json_data = json.dumps(data)

    # Send the POST request with the JSON data
    response = requests.post(url, headers=headers, data=json_data)

    # Check the response status code
    if response.status_code == 200:
        # Successful request
        st.write("Request was successful.")
            # Decode the response content using utf-8-sig

        csv_str = response.content.decode("utf-8")

        # print("\n\n",type(csv_str))
        
        df = pd.DataFrame([x.split(';') for x in csv_str.split('\n')])
        # Print the parsed JSON response
        print("\n\n",df)
        return df
    else:
        # Unsuccessful request
        st.write(f"Request failed with status code: {response.status_code}")
        st.write("Response content:", response.text)
        return None

    
    
