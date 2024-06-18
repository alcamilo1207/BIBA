import json
import math
import pickle
import requests
import numpy as np
import random as rd
import pandas as pd
import streamlit as st
import matplotlib as mpl
import matplotlib.cm as cm
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

class Job:
    def __init__(self,id,wt,size):
        self.id = id
        self.wt = wt
        self.size = size
        self.completed = False
        self.hold = False

    def __str__(self):
        return f"Job {self.id}, wt: {self.wt}, size: {self.size}"


class Machine:
    def __init__(self,id,speed,EU):
        self.id = id
        self.speed = speed
        self.EU = EU
        self.time = 0

    def __str__(self):
        return f"Machine {self.id}, speed: {self.speed}, EU: {self.EU}"


class Item:
    def __init__(self,id,job,machine,duration):
        self.id = id
        self.job = job
        self.machine = machine
        self.duration = duration


class Scheduler:
    """
    Generates daily schedules with synthetic data.
    -> Time resolution: 1 minute
    """
    def __init__(self):
        self.n_jobs = 0
        self.n_machines = 0
        self.jobs = []
        self.machines = []
        self.schedule = []

    def __str__(self):
        return f" sch_length: {len(self.schedule)}, jobs {self.n_jobs}, Machines: {self.n_machines}"

    def load(self,filename="scheduler"):
        with open(f'{filename}.pkl', 'rb') as file:
            loaded_object = pickle.load(file)

        print(" Scheduler has been loaded.")
        return loaded_object

    def save(self,filename="scheduler"):
        with open(f'{filename}.pkl', 'wb') as file:
            pickle.dump(self, file)

        print("Scheduler has been saved.")

    def create_job(self):
        wt = rd.randint(0,1440*3)
        size = rd.uniform(100,300)
        self.n_jobs += 1
        self.jobs.append(Job(self.n_jobs,wt,size))

    def create_machine(self):
        speed = rd.uniform(0.75,1.25)
        EU = rd.uniform(0.5,1.5)
        self.n_machines += 1
        self.machines.append(Machine(self.n_machines-1,speed,EU))

    def get_pending_jobs(self):
        jobs = self.jobs
        pending_jobs = []
        for j in jobs:
            if j.completed == False and j.hold == False:
                pending_jobs.append(j)
        
        return pending_jobs

    def get_duration(self,job, machine):
        size = job.size
        speed = machine.speed
        return math.ceil(size/speed)
    
    def get_total_EU(self,job, machine):
        size = job.size
        EU = machine.EU
        return size*EU

    def convert_minutes_to_timestamp(self,minutes):
        # Define the start date
        start_date = datetime(2024, 1, 1)

        # Create a timedelta object for the given minutes
        time_delta = timedelta(minutes=minutes)

        # Calculate the new timestamp by adding the timedelta to the start date
        new_timestamp = start_date + time_delta

        # Return the new timestamp
        return new_timestamp

    def schedule_job(self,job, machine,idle_prob=0.1):
        if rd.random() > idle_prob:
            j_id = job.id
            j_size = job.size
            m_id = machine.id
            total_EU = self.get_total_EU(job, machine)
            start_timestamp = machine.time
            machine.time += self.get_duration(job, machine)
            self.schedule.append([j_id, m_id, start_timestamp, self.get_duration(job, machine), total_EU,j_size])
            job.completed = True
        else:  # Idling job
            m_id = machine.id
            start_timestamp = machine.time
            duration = math.ceil(rd.uniform(50,300))
            if machine.time + duration < 1440:
                machine.time += duration
            else:
                duration = 1440 - machine.time
                machine.time += duration
            self.schedule.append([0, m_id, start_timestamp, duration, 0.0, 0.0])

    def plot_schedule(self):
        fig, ax = plt.subplots()
        ax.invert_yaxis()
        ax.set_xlabel("Time [minutes]")
        ax.set_xlim(0,1440)
        cmap = cm.plasma # choose a colormap

        total_EUs = np.array([item[4] for item in self.schedule])

        norm = mpl.colors.Normalize(vmin=min(total_EUs), vmax=max(total_EUs)) # Normalizer

        # Get the schedule data for each machine
        ids = np.array([item[0] for item in self.schedule])
        starts = np.array([item[2] for item in self.schedule])
        times = np.array([item[3] for item in self.schedule])
        total_EUs = np.array([item[4] for item in self.schedule])

        # Generate the data for the plot
        m = self.machines
        labels = [f"Machine {i[1]} \n [Speed: {m[i[1]].speed:.2}, EU: {m[i[1]].EU:.2}]" for i in self.schedule]
        for (id,label,time,total_EU,start) in zip(ids,labels,times,total_EUs,starts):
            if total_EU < 0.5*max(total_EUs):
                text_color = "white"
            else:
                text_color = "black"

            ax.barh(label,time,left=start, height=0.5,color=cmap(norm(total_EU)),edgecolor="white",label=id)
            ax.text(start + time / 2, label, f'{id}', va='center', ha='center', color=text_color)
            
        fig.colorbar(cm.ScalarMappable(norm=norm, cmap=cmap), ax=ax, label="Energy usage [kWh]")
        plt.subplots_adjust(
            top = 0.88,
            bottom = 0.155,
            left = 0.22,
            right = 1.0,
            hspace = 0.2,
            wspace = 0.2)
        plt.show()
        return fig

    def get_schedule(self):
        sch = self.schedule
        new_sch = [[f"machine {i[1]}",i[4],f"job {i[0]}",i[5],self.convert_minutes_to_timestamp(i[2]),i[3]] for i in sch]
        cols = ['assigned_to','energy','name','size','start_timestamp','actual_duration_int']
        df = pd.DataFrame(new_sch,columns=cols)
        return df

    def create_schedule(self,method=None,idle_prob=0.15):
        """
        Generate schedule for all machines using synthetic data
        """
        if method == "random":
            print(f"Generating schedule using \"{method}\" order.")
        else:
            print(f"Generating schedule using \"sequential\" order.")


        self.schedule = []    
        machines = self.machines

        pending_jobs = self.get_pending_jobs()
        while len(pending_jobs) > 0:  # Loop until the scheduling end condition is met
            for j in pending_jobs: # Loop through each pending job
                # job selection method
                if method == "priority":
                    pass

                elif method == "random":
                    pick = rd.randint(0,len(pending_jobs)-1)
                    j = pending_jobs[pick]
                else:
                    pass

                times = [m.time for m in machines]

                for i, m in enumerate(machines):  # look for a machine for the specific jop
                    # Check if the machine is available
                    if m.time == 0 or m.time == min(times):
                        # Check if the work can be done before the end of the day
                        if m.time + self.get_duration(j, m) < 1440:
                            self.schedule_job(j, m,idle_prob)
                            break
                        else:
                            # Check for another that can accomplish the work before the end of the day
                            for i, m in enumerate(machines):
                                if m.time + self.get_duration(j, m) < 1440:
                                    self.schedule_job(j, m,idle_prob)
                                    break

                            j.hold = True

                pending_jobs = self.get_pending_jobs()
                break

    def main(self, n_jobs,n_machines, choice, method=None,idle_prob = 0.15):
        ## Load or create an schedule from scratch
        if choice == "load":
            self.load()
            #sch1 = Scheduler.load()
        elif choice == "create":
            #sch1 = Scheduler() # Create scheduler object
        
            for i in range(n_jobs): self.create_job() # Create job with radom parameters

            for i in range(n_machines): self.create_machine() # Create machine with radom parameters
        
            print("Jobs and machines gerated with random paremeters!")
            self.save()
        else:
            print("Invalid option")
            return None

        self.create_schedule(method,idle_prob) # Create schedule and store it            


class EnergyPrices:
    def __init__(self, region):
        self.region = region

    def get_price_at_minute(hourly_price_values,minute):
        h = int(minute/1440)
        price = hourly_price_values[h]
        return price

    def create_empty_energy_prices_df(self, start_datetime):
        date_range_start = pd.date_range(start_datetime.strftime("%Y/%m/%d"), periods=24, freq='h')
        date_range_end = pd.date_range(start=date_range_start[1], periods=24, freq='h')
        df = pd.DataFrame(np.full((24,3),0.0),columns=['Start date','End date', self.region])
        df['Start date'] = date_range_start
        df['End date'] = date_range_end
        return df

    def get_prices(self, date):
        """"
        Request energy marked data through the www.smard.de API.
        """

        # Define the URL to send the request to
        url = 'https://www.smard.de/nip-download-manager/nip/download/market-data'  # Replace with the actual URL

        # Define the headers for the request
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json, text/plain, */*'
        }

        # Get the current day datetime starting at 00:00 hours
        picked_day = datetime(date.year, date.month, date.day)

        # Get the next day datetime starting at 00:00 hours (2 hours shift corrected)
        start_datetime = picked_day + timedelta(days=1) #- timedelta(hours=2)
        print("start_datetime",start_datetime)
        st.write(start_datetime)

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
            df = pd.DataFrame(list[1:-1])

            # Check if dataset is empty
            if df.iloc[0,0] == 'No data for submitted query\r':
                return self.create_empty_energy_prices_df(start_datetime)

            # Adding the headings
            df.columns = list[0][:df.shape[1]]

            return df
        else:
            # Unsuccessful request
            st.write(f"Request failed with status code: {response.status_code}")
            st.write("Response content:", response.text)
            return self.create_empty_energy_prices_df(start_datetime)

    def calculate_energy_cost(self, prices_df, job_schedule, power_schedule):
        # Start all the output variables at zero to avoid unassigned variables
        performance, total_cost, total_energy, total_production, total_number_of_jobs = 0,0,0,0,0 
        
        # Getting variables for internal operations
        power_values = power_schedule.values/(60*1000)
        energies = job_schedule['energy'].values
        sizes = job_schedule['size'].values

        # Counting number of jobs
        for size in sizes:
            if size > 0:
                total_number_of_jobs += 1

        total_production += sizes.sum()
        total_energy += energies.sum()

        # First check if the dataframe has the right shape
        if prices_df.shape == (24,19):
            prices_str = prices_df[self.region].values
            try:
                # Convert prices array values from strings to floats
                prices = [float(item) for item in prices_str]
                total_cost += np.sum([pow[0]*self.get_price_at_minute(prices,min) for min, pow in enumerate(power_values)])
                performance += total_production/(total_energy*total_cost)
            except Exception as e:
                if str(e) == "could not convert string to float: '-'":
                    print("Day-ahead prices not available")
                else:
                    print(e)

        return performance, total_cost, total_energy, total_production, total_number_of_jobs


class Helper:
    def create_scheduler(filename="saved_sch",n_jobs=50, n_machines=3):
        sch_object = Scheduler()
        sch_object.main(n_jobs,n_machines,"create","")
        scheduler = sch_object.load()
        scheduler.create_schedule()
        scheduler.save()
        return scheduler

    def load_scheduler(filename="saved_sch"):
        sch_object = Scheduler()
        scheduler = sch_object.load()
        return scheduler

    def get_scheduler(self,load,verbose=False):
        if load:
            try:
                scheduler = self.load_scheduler()
            except Exception as e:
                st.write(e)
                print(e)
                scheduler = self.create_scheduler()
        else:
            scheduler = self.create_scheduler()

        schedule = scheduler.schedule
        df = scheduler.get_schedule()

        # Getting the energy usage
        total_energy_usage = np.array([item[4] for item in schedule]).sum()

        # Calculating electricity cost
        energy_price = 0.3 # Euros/kWh
        total_cost = total_energy_usage*energy_price # Euros

        if verbose:
            print(df)
            print(f"Total energy usage: {total_energy_usage:.6} kWh\nTotal cost: {total_cost:.6} Euros")

        return scheduler

    def timestamp_to_dayminutes(self,timestamp,duration):
        start = timestamp.hour*60+timestamp.minute
        end = start + duration
        return [start,end]

    def get_power(self,scheduler):
        schedule = scheduler.get_schedule()
        schedule["start_timestamp"] = pd.to_datetime(schedule["start_timestamp"])
        power_schedules = []
        for i,m in enumerate(scheduler.machines):
            m_label = f"machine {i}"
            m_schedule = schedule[schedule["assigned_to"] == m_label]
            idle_times = m_schedule[m_schedule["name"] == "job 0"]
            it_int = [self.timestamp_to_dayminutes(start, duration) for start, duration in zip(idle_times["start_timestamp"],idle_times["actual_duration_int"])]
            m_power = m.speed * m.EU
            m_pw_sch = np.full(1440, m_power)
            if len(it_int)>0:
                for it in it_int:
                    start,end = it[0],it[1]
                    m_pw_sch[start:end] = 0.0

            power_schedules.append(m_pw_sch)

        total_power = np.copy(power_schedules[0])
        for i in range(1,len(power_schedules)):
            total_power += power_schedules[i]

        power_schedules.append(total_power)
        df = pd.DataFrame(np.transpose(power_schedules))
        return df

# shelp = Helper()
# scheduler = shelp.get_scheduler(load=True)
# df = shelp.get_power(scheduler)
# print(df)

