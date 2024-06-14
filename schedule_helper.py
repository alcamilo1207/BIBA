import scheduler as sh
import numpy as np

load = False

def get_schedulePlot():
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
    print(df)

    # Getting the energy usage
    total_energy_usage = np.array([item[4] for item in schedule]).sum()

    # Calculating electricity cost
    energy_price = 0.3 # Euros/kWh
    total_cost = total_energy_usage*energy_price # Euros

    print(f"Total energy usage: {total_energy_usage:.6} kWh\nTotal cost: {total_cost:.6} Euros")

    return scheduler.plot_schedule()