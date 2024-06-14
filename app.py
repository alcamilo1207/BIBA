import streamlit as st
import json_req as jr


def main():
    st.set_page_config(layout="wide")

    st.subheader("Day-ahead energy prices forecast")

    menu = ["Inicio","Sobre nosotros"]

    choice = st.sidebar.selectbox("Menu",menu)

    if choice == "Inicio":
        info = """
            Data source: Bundesnetzagentur | SMARD.de\nSMARD receives the data directly from the European Network of Transmission System Operators for Electricity (ENTSO-E). \nOnly data verified by the Bundesnetzagentur is published on SMARD. \nThe Bundesnetzagentur is constantly exchanging information with the transmission network operators (TSOs) in order to continuously improve data quality.https://www.smard.de/en/datennutzung
        """
        st.write(info)
        # Create a dataframe
        df = jr.get_prices()
        st.dataframe(df)
    else:
        st.subheader("Data")




if __name__ == "__main__":
    main()