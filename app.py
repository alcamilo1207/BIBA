import streamlit as st
import json_req as jr
import schedule_helper as shelp
import mpld3
import streamlit.components.v1 as components


def main():
    menu = ["Energy prices data","Scheduler"]

    choice = st.sidebar.selectbox("Menu",menu)

    if choice == "Inicio":
        st.subheader("Day-ahead energy prices forecast")
        st.write("Data source: Bundesnetzagentur | SMARD.de. More info: https://www.smard.de/en/datennutzung")
        # Create a dataframe
        df = jr.get_prices()
        st.dataframe(df)

    else:
        st.subheader("Data")
        fig = shelp.get_schedulePlot()
        fig_html = mpld3.fig_to_html(fig)
        components.html(fig_html, width=1200,height=600)
        #st.pyplot(fig,use_container_width=True)




if __name__ == "__main__":
    main()