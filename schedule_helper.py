import scheduler as sh
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

load = True

def get_scheduler(verbose=False):
    sch_object = sh.Scheduler()
    if load:
        scheduler = sch_object.load("saved_sch")
    else:
        sh.main(50,3,"create","")
        scheduler = sch_object.load()
        scheduler.create_schedule()
        scheduler.save("saved_sch")

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

def timestamp_to_dayminutes(timestamp,duration):
    start = timestamp.hour*60+timestamp.minute
    end = start + duration
    return [start,end]

def get_power(scheduler):
    schedule = scheduler.get_schedule()
    schedule["start_timestamp"] = pd.to_datetime(schedule["start_timestamp"])
    power_schedules = []
    for i,m in enumerate(scheduler.machines):
        m_label = f"machine {i}"
        m_schedule = schedule[schedule["assigned_to"] == m_label]
        idle_times = m_schedule[m_schedule["name"] == "job 0"]
        it_int = [timestamp_to_dayminutes(start, duration) for start, duration in zip(idle_times["start_timestamp"],idle_times["actual_duration_int"])]
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

scheduler = get_scheduler()
df = get_power(scheduler)
print(df[3])

