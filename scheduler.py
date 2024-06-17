import random as rd
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib as mpl
import numpy as np
import pandas as pd
import pickle
from datetime import datetime, timedelta
import math
import os

os.system('cls' if os.name == 'nt' else 'clear')


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


def main(n_jobs,n_machines, choice,method=None,idle_prob = 0.15):
    ## Load or create an schedule from scratch
    if choice == "load":
        sch1 = Scheduler.load()
    elif choice == "create":
        sch1 = Scheduler() # Create scheduler object
    
        for i in range(n_jobs): sch1.create_job() # Create job with radom parameters

        for i in range(n_machines): sch1.create_machine() # Create machine with radom parameters
    
        print("Jobs and machines gerated with random paremeters!")
        sch1.save()
    else:
        print("Invalid option")
        return None

    sch1.create_schedule(method,idle_prob) # Create schedule and store it
