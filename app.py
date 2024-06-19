import pandas as pd
import streamlit as st
import json_req as jr
import schedule_helper as shelp
import plotly.graph_objects as go
import matplotlib.cm as cm
import matplotlib as mpl
import numpy as np
import plotly.express as px
from datetime import datetime, timedelta
from millify import millify, prettify
import locale
locale.setlocale(locale.LC_ALL, 'de_DE.UTF-8')

st.set_page_config(layout='wide')

def duration_to_color(all_durations, duration):
    cmap = cm.plasma  # choose a colormap
    norm = mpl.colors.Normalize(vmin=min(all_durations), vmax=max(all_durations))  # Normalizer
    c = cmap(norm(duration))
    color = f"rgb({c[0]*255}, {c[1]*255}, {c[2]*255}, {c[3]})"
    return color

def main():
    st.sidebar.title("User input data")
    generate = st.sidebar.button(label="Generate random schedule",use_container_width=True)
    #fixed_price = st.sidebar.checkbox(label="Fixed energy price?")
    current_hour = datetime.now().hour
    if current_hour > 15:
        date_pick = st.sidebar.date_input(label="Select date") #,value=datetime.fromisoformat("2024-06-16")
    else:
        date_pick = st.sidebar.date_input(label="Select date",value=datetime.now()-timedelta(days=1)) #+timedelta(days=1)

    #sb_container = st.sidebar.container(border=True)
    # with sb_container:
    #     if fixed_price:
    #         fixed_price_value = st.number_input(label="Energy price value",min_value=0.00,step=0.01)
    #     else:
    #         pass

    # Scheduler data
    if generate:
        scheduler = shelp.get_scheduler(load=False)

    else:
        scheduler = shelp.get_scheduler(load=True)

    sch_df = scheduler.get_schedule()

    # power data
    pw_df = shelp.get_power(scheduler)

    # Energy prices data
    prices_df = jr.get_prices(date_pick)

    # Metrics
    performance, total_cost, total_energy, total_production, total_number_of_jobs = jr.calculate_energy_cost(prices_df, sch_df, pw_df[[pw_df.columns[-1]]])

    #Scheduler plot
    dates = pd.date_range(datetime.now().strftime("%Y-%m-%d"), periods=12, freq='2h')
    x_values = [i*60*2 for i in range(12)]
    x_values3 = [prices_df['Start date'][i*2] for i in range(12)]

    fig1 = px.bar(sch_df,
                 y="assigned_to",
                 x="actual_duration_int",
                 color="energy",
                 orientation="h",
                 #color_continuous_scale='inferno',
                 hover_name="name",
                 labels={
                     "assigned_to": "assigned to",
                     "actual_duration_int": "",
                     "energy": "energy [kWh]",
                 },
                title="Day-ahead schedule")

    fig1.update_xaxes(tickvals=x_values, ticktext=[d.strftime('%H:00') for d in dates])
    fig1.update_traces(width=.9)
    fig1.update_coloraxes(colorbar={'orientation':'h', 'thickness':15, 'y': 1.1})
    fig1.update_layout(height=300,
            margin=dict(
            l=0,
            r=0,
            b=25,
            t=0,
            pad=10
        ),)

    fig2 = go.Figure()

    for i in range(pw_df.shape[1]):
        if i == pw_df.shape[1]-1:
            name = f"Total power"
            fig2.add_trace(go.Scatter(
                name=name,
                x=pw_df.index.values,
                y=pw_df[i],
                line=dict(color='black', width=4, dash='dot')
            ))
        else:
            name = f"machine {i}"
            fig2.add_trace(go.Scatter(
                name=name,
                x=pw_df.index.values,
                y=pw_df[i],
                fill='tozeroy',
            ))

    fig2.update_xaxes(tickvals=x_values, ticktext=[d.strftime('%H:00') for d in dates])
    fig2.update_layout(
        height=300,
        title="Factory total power",
        yaxis_title="Power [kW]",
        margin=dict(
            l=95,
            r=30,
            b=0,
            t=50,
            pad=4
        ),
        legend=dict(
            orientation='h',
            yanchor="top",
            y=-0.3,
            xanchor="left",
            x=0
        )
    )

    fig3 = px.area(prices_df,x="Start date", y="Germany/Luxembourg [€/MWh] Original resolutions",line_shape='hv',title="Energy prices")
    fig3.update_xaxes(tickvals=x_values3, ticktext=[d.strftime('%H:00') for d in dates])

    # View in UI
    with st.container():
        # Your container content here
        #Schedule
        st.subheader("Day-ahead job schedule and energy prices forecast")

        row1 = st.columns(2)
        row2 = st.columns(3)
        metrics = [
            {"label": "Scheduler performance (production/(energy × cost))", "value": locale.format_string("%.2f kg/(kWh × €)",performance)},
            {"label": "Total energy cost", "value": locale.format_string("%.2f €",total_cost)},
            {"label": "Total energy usage", "value": locale.format_string("%.2f kWh",total_energy)},
            {"label": "Total production", "value": locale.format_string("%.0f kg",total_production)},
            {"label": "Total jobs completed", "value": f"{total_number_of_jobs} jobs"},
        ]
        for i,col in enumerate((row1 + row2)):
            cont = col.container(height=120)
            cont.metric(metrics[i]["label"],metrics[i]["value"],)

        st.plotly_chart(fig1,use_container_width=True)
        with st.expander("Machine parameters"):
            m_params = pd.DataFrame([[m.id,m.speed,m.EU] for m in scheduler.machines],columns=['Machine','Speed [kg/min]','Energy usage [kWh/min]'])
            m_params.set_index('Machine')
            st.dataframe(m_params,hide_index=True)

        st.plotly_chart(fig2, use_container_width=True)

        # Energy prices Data
        st.plotly_chart(fig3, use_container_width=True)

        data_cols = st.columns([1, 3])

        with data_cols[0]:
            st.write("Schedule dataframe")
            st.dataframe(sch_df)
            st.write("Artificially generated")
        with data_cols[1]:
            st.write("Energy prices dataframe.")
            st.dataframe(prices_df)
            st.write("Data source: Bundesnetzagentur | SMARD.de. More info: https://www.smard.de/en/datennutzung")


if __name__ == "__main__":
    main()