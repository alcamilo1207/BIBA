import requests
import json
import pandas as pd
import streamlit as st
from datetime import datetime,timedelta
import numpy as np

def get_prices(date):
    # Define the URL to send the request to
    url = 'https://www.smard.de/nip-download-manager/nip/download/market-data'  # Replace with the actual URL

    # Define the headers for the request
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json, text/plain, */*'
    }

    # Get the current day datetime starting at 00:00 hours
    current_day = datetime(date.year, date.month, date.day, 0, 0, 0)

    # Get the next day datetime starting at 00:00 hours (2 hours shift corrected)
    start_datetime = current_day + timedelta(days=1) #- timedelta(hours=2)

    # Get the other next day datetime starting at 00:00 hours
    end_datetime = start_datetime + timedelta(days=1)

    # Converting datetime to integer format
    start_date = int(start_datetime.timestamp()*1000)
    end_date = int(end_datetime.timestamp()*1000)


    # Define the data to be sent in the request
    data = {"request_form":[{"format":"CSV","moduleIds":[8004169,8004170,8000251,8005078,8000252,8000253,8000254,8000255,8000256,8000257,8000258,8000259,8000260,8000261,8000262,8004996,8004997],"region":"DE","timestamp_from":start_date,"timestamp_to":end_date,"type":"discrete","language":"en","resolution":"hour"}]}

    # Convert the data dictionary to a JSON string
    json_data = json.dumps(data)

    # Send the POST request with the JSON data
    response = requests.post(url, headers=headers, data=json_data)

    # Check the response status code
    if response.status_code == 200:
        # Successful request
            
        # Decode the response content using utf-8-sig
        csv_str = response.content.decode("utf-8")
        list = [x.split(';') for x in csv_str.split('\n')]
        list[0][0] = 'Start date'
        # Convert string to data frame
        df = pd.DataFrame(list[1:])

        # Dropping last row
        print(list[0])
        df.columns = list[0]
        df = df.drop(df.index[-1])
        #df = df.drop(df.index[0])

        return df
    else:
        # Unsuccessful request
        st.write(f"Request failed with status code: {response.status_code}")
        st.write("Response content:", response.text)
        return None

def get_price_at_minute(price_hourly_values,minute):
    h = int(minute/1440)
    price = price_hourly_values[h]
    return price

def calculate_energy_cost(date,job_schedule,power_schedule):
    df = get_prices(date)
    prices_str = df['Germany/Luxembourg [€/MWh] Original resolutions'].values
    try:
        prices = [float(item) for item in prices_str]
    except Exception as e:
        if str(e) == "could not convert string to float: '-'":
            return "Not available"
        else:
            return str(e)

    power_values = power_schedule.values/(60*1000)
    energies = job_schedule['energy'].values
    sizes = job_schedule['size'].values

    total_cost = np.sum([pow[0]*get_price_at_minute(prices,min) for min, pow in enumerate(power_values)])

    total_number_of_jobs = 0
    for size in sizes:
        if size > 0:
            total_number_of_jobs += 1

    total_production = sizes.sum()
    total_energy = energies.sum()

    performance = total_cost/total_production
    return performance, total_cost, total_energy, total_production, total_number_of_jobs
