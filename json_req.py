import requests
import json
import pandas as pd
import streamlit as st

def get_pries():
    # Define the URL to send the request to
    url = 'https://www.smard.de/nip-download-manager/nip/download/market-data'  # Replace with the actual URL

    # Define the headers for the request
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json, text/plain, */*'
    }

    # Define the data to be sent in the request
    data = {"request_form":[{"format":"CSV","moduleIds":[8004169,8004170,8000251,8005078,8000252,8000253,8000254,8000255,8000256,8000257,8000258,8000259,8000260,8000261,8000262,8004996,8004997],"region":"DE-LU","timestamp_from":1718056800000,"timestamp_to":1719007200000,"type":"discrete","language":"en","resolution":"day"}]}

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

    
    
