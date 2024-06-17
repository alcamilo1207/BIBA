import pandas as pd
import streamlit as st
import json_req as jr
import schedule_helper as shelp
import plotly.graph_objects as go
import matplotlib.cm as cm
import matplotlib as mpl
import numpy as np
import plotly.express as px
from datetime import datetime,timedelta

st.set_page_config(layout='wide')

def duration_to_color(all_durations, duration):
    cmap = cm.plasma  # choose a colormap
    norm = mpl.colors.Normalize(vmin=min(all_durations), vmax=max(all_durations))  # Normalizer
    c = cmap(norm(duration))
    color = f"rgb({c[0]*255}, {c[1]*255}, {c[2]*255}, {c[3]})"
    return color

def main():
    generate = st.sidebar.button(label="Generate random schedule")

    date_pick = st.sidebar.date_input(label="Select date")

    st.subheader("Data")

    # Scheduler data
    if generate:
        scheduler = shelp.get_scheduler(load=False)

    else:
        scheduler = shelp.get_scheduler(load=True)

    sch_df = scheduler.get_schedule()

    # power data
    pw_df = shelp.get_power(scheduler)

    #Scheduler plot

    dates = pd.date_range('2022-01-01', periods=12, freq='2H')
    x_values = [i*60*2 for i in range(12)]

    fig1 = px.bar(sch_df,
                 y="assigned_to",
                 x="actual_duration_int",
                 color="energy",
                 orientation="h",
                 color_continuous_scale='inferno',
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
        else:
            name = f"machine {i}"

        fig2.add_trace(go.Scatter(
            name=name,
            x=pw_df.index.values,
            y=pw_df[i],
            fill='tozeroy',
        ))

    #'rgba(31,119,180,0.5)

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

    # View in UI
    with st.container():
        # Your container content here
        st.plotly_chart(fig1,use_container_width=True)

        st.plotly_chart(fig2, use_container_width=True)

        st.write("Schedule Dataset")
        st.dataframe(sch_df)

        # Data
        st.subheader("Day-ahead energy prices forecast")
        st.write("Data source: Bundesnetzagentur | SMARD.de. More info: https://www.smard.de/en/datennutzung")
        data_df = jr.get_prices(date_pick)
        st.dataframe(data_df)




if __name__ == "__main__":
    main()